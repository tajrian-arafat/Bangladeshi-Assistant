"""Sync research staging claims into DB and publish only gate-eligible VERIFIED claims."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.knowledge.publication_gate import (
    assert_mapping_safe,
    can_populate_fee,
    can_populate_must_need,
    can_populate_procedure_step,
    evaluate_official_publication,
)
from app.core.exceptions import ValidationError
from app.domain.enums import (
    CatalogueMappingReviewStatus,
    ClaimPipelineStatus,
    ClaimType,
    InformationClass,
    KnowledgeGapPriority,
    KnowledgeGapStatus,
    KnowledgeGapType,
)
from app.domain.models.claims import (
    Claim,
    ClaimEvidence,
    KnowledgeGap,
    ServiceCatalogueMapping,
)
from app.domain.models.knowledge import (
    ChecklistItem,
    Fee,
    Procedure,
    ProcedureStep,
    Service,
    Source,
    SourceVersion,
)
from app.domain.models.operations import AuditLog


MVP_SEED_SLUGS = {
    "passport-renewal",
    "nid-correction",
    "driving-licence-renewal",
    "birth-registration",
    "tin-registration",
}


@dataclass
class PublishReport:
    dry_run: bool
    batch_id: str
    actions: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    published_fees: int = 0
    published_checklist: int = 0
    published_steps: int = 0
    synced_claims: int = 0
    skipped: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


class KnowledgePublisher:
    def __init__(
        self,
        session: AsyncSession,
        *,
        repo_root: Path,
        dry_run: bool = True,
    ) -> None:
        self.session = session
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.staging_root = repo_root / "data" / "research" / "staging"

    def staging_dir(self, batch_id: str) -> Path:
        # accept batch-01 or batch-01-identity-civil-registration
        candidates = [
            self.staging_root / batch_id,
            self.staging_root / "batch-01" if batch_id.startswith("batch-01") else None,
        ]
        for c in candidates:
            if c and c.exists():
                return c
        raise FileNotFoundError(f"Staging batch not found: {batch_id}")

    async def _audit(self, action: str, resource_type: str, resource_id: str, after: dict) -> None:
        if self.dry_run:
            return
        self.session.add(
            AuditLog(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                after_json=after,
            )
        )

    async def load_mappings(self) -> dict[str, dict[str, Any]]:
        path = self.repo_root / "data" / "research" / "catalogue_runtime_mappings.json"
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return {m["catalogue_service_id"]: m for m in data.get("mappings", [])}

    async def resolve_runtime_service(
        self,
        catalogue_service_id: str,
        mapping_file: dict[str, dict[str, Any]],
        report: PublishReport,
    ) -> Service | None:
        mapping = mapping_file.get(catalogue_service_id)
        if not mapping:
            report.errors.append(
                f"No catalogue→runtime mapping for {catalogue_service_id}; refusing publish"
            )
            return None

        slug = mapping.get("runtime_slug")
        if not slug:
            if mapping.get("mapping_type") == "new_canonical":
                report.skipped += 1
                report.actions.append(
                    {
                        "action": "skip_uncreated_service",
                        "catalogue_service_id": catalogue_service_id,
                        "reason": "new_canonical runtime service not created yet",
                    }
                )
                return None
            report.errors.append(f"Mapping for {catalogue_service_id} missing runtime_slug")
            return None

        result = await self.session.execute(select(Service).where(Service.slug == slug))
        service = result.scalar_one_or_none()
        if not service:
            report.errors.append(
                f"Runtime service slug={slug} not found for {catalogue_service_id}"
            )
            return None

        gate = assert_mapping_safe(
            catalogue_service_id=catalogue_service_id,
            expected_runtime_slug=slug,
            actual_runtime_slug=service.slug,
            mapping_review_status=mapping.get("review_status", "PENDING"),
            allow_overwrite_seed=bool(mapping.get("allow_overwrite_seed", False)),
            target_is_mvp_seed=service.slug in MVP_SEED_SLUGS,
        )
        # Mapping safety for *publication overwrite* of seed fields:
        # syncing claims into DB is OK; overwriting checklist/fees on MVP seed is not
        # unless allow_overwrite_seed.
        if not gate.allowed and any("silently overwritten" in r for r in gate.reasons):
            # Still return service for claim sync; publish path checks allow_overwrite_seed
            pass
        elif not gate.allowed and "wrong service" in " ".join(gate.reasons):
            report.errors.extend(gate.reasons)
            return None

        return service

    async def sync_claims_from_staging(self, batch_id: str) -> PublishReport:
        """Upsert Source/SourceVersion/Claim/Evidence/Gaps. Never auto-VERIFIES."""
        report = PublishReport(dry_run=self.dry_run, batch_id=batch_id)
        staging = self.staging_dir(batch_id)
        sources = json.loads((staging / "sources.json").read_text(encoding="utf-8"))["sources"]
        versions = json.loads((staging / "source_versions.json").read_text(encoding="utf-8"))[
            "source_versions"
        ]
        claims = json.loads((staging / "claims.json").read_text(encoding="utf-8"))["claims"]
        evidence = json.loads((staging / "evidence.json").read_text(encoding="utf-8"))["evidence"]
        mappings = await self.load_mappings()

        # Ensure mappings cannot invent VERIFIED
        for c in claims:
            if c.get("pipeline_status") == ClaimPipelineStatus.VERIFIED.value:
                report.errors.append(
                    f"Staging claim {c.get('claim_id')} has VERIFIED status; "
                    "research must not auto-verify. Demote before sync."
                )
        if report.errors:
            return report

        source_id_map: dict[str, UUID] = {}
        version_id_map: dict[str, UUID] = {}

        for s in sources:
            domain = s.get("domain") or urlparse(s.get("source_url", "")).netloc
            existing = await self.session.execute(
                select(Source).where(Source.domain == domain, Source.title == s.get("source_title"))
            )
            row = existing.scalar_one_or_none()
            if not row:
                # also match by domain alone if title differs
                existing2 = await self.session.execute(
                    select(Source).where(Source.domain == domain).limit(1)
                )
                row = existing2.scalar_one_or_none()
            if not row:
                if self.dry_run:
                    source_id_map[s["source_id"]] = uuid4()
                    report.actions.append({"action": "would_create_source", "domain": domain})
                    continue
                row = Source(
                    domain=domain or "unknown",
                    title=s.get("source_title"),
                    tier=int(s.get("authority_tier") or 6),
                )
                self.session.add(row)
                await self.session.flush()
            else:
                # Never auto-change authority tier by LLM/script if already set differently
                # Only set if missing/default — keep existing tier
                pass
            source_id_map[s["source_id"]] = row.id

        for v in versions:
            sid = source_id_map.get(v["source_id"])
            if not sid:
                continue
            if self.dry_run:
                version_id_map[v["source_version_id"]] = uuid4()
                report.actions.append(
                    {
                        "action": "would_create_source_version",
                        "url": v.get("url"),
                        "content_hash": v.get("content_hash"),
                    }
                )
                continue
            existing = await self.session.execute(
                select(SourceVersion).where(
                    SourceVersion.source_id == sid, SourceVersion.url == v["url"]
                )
            )
            row = existing.scalar_one_or_none()
            if not row:
                row = SourceVersion(
                    source_id=sid,
                    url=v["url"],
                    canonical_url=v.get("canonical_url") or v["url"],
                    content_hash=v.get("content_hash"),
                    retrieved_at=_parse_iso(v.get("retrieved_at")),
                    fetched_at=_parse_iso(v.get("retrieved_at")),
                    retrieval_method=v.get("fetched_method") or v.get("retrieval_method"),
                    http_status=v.get("http_status"),
                    title=None,
                    raw_content_path=v.get("raw_pointer"),
                    metadata_json={"research_source_version_id": v["source_version_id"]},
                )
                self.session.add(row)
                await self.session.flush()
            version_id_map[v["source_version_id"]] = row.id

        evidence_by_claim: dict[str, list[dict]] = {}
        for e in evidence:
            evidence_by_claim.setdefault(e["claim_id"], []).append(e)

        for c in claims:
            catalogue_id = c.get("service_id")
            if not catalogue_id:
                continue
            service = await self.resolve_runtime_service(catalogue_id, mappings, report)
            if not service:
                # For new_canonical without runtime row, skip without hard error if already noted
                continue

            status = c.get("pipeline_status") or ClaimPipelineStatus.DISCOVERED.value
            if status == ClaimPipelineStatus.VERIFIED.value:
                report.errors.append(f"Refusing to sync auto-VERIFIED claim {c['claim_id']}")
                continue

            research_key = c["claim_id"]
            if self.dry_run:
                report.synced_claims += 1
                report.actions.append(
                    {
                        "action": "would_upsert_claim",
                        "research_claim_key": research_key,
                        "pipeline_status": status,
                        "runtime_slug": service.slug,
                    }
                )
                continue

            existing = await self.session.execute(
                select(Claim).where(
                    Claim.service_id == service.id, Claim.research_claim_key == research_key
                )
            )
            claim = existing.scalar_one_or_none()
            subject, predicate = _split_claim(c.get("claim_text") or c.get("claim") or "")
            if not claim:
                claim = Claim(
                    service_id=service.id,
                    research_claim_key=research_key,
                    claim_type=_map_claim_type(c),
                    subject=subject,
                    predicate=predicate,
                    value=c.get("claim_text") or c.get("claim") or "",
                    structured_value=c.get("structured_value"),
                    information_class=c.get("information_class") or InformationClass.DISCOVERY.value,
                    pipeline_status=status,
                    confidence=c.get("confidence"),
                )
                self.session.add(claim)
                await self.session.flush()
            else:
                # Do not upgrade status toward VERIFIED via sync
                claim.pipeline_status = status
                claim.confidence = c.get("confidence")
                claim.value = c.get("claim_text") or claim.value
                claim.information_class = (
                    c.get("information_class") or claim.information_class
                )

            for e in evidence_by_claim.get(research_key, []):
                svid = version_id_map.get(e.get("source_version_id"))
                if not svid:
                    continue
                existing_ev = await self.session.execute(
                    select(ClaimEvidence).where(
                        ClaimEvidence.claim_id == claim.id,
                        ClaimEvidence.source_version_id == svid,
                    )
                )
                if existing_ev.scalar_one_or_none():
                    continue
                self.session.add(
                    ClaimEvidence(
                        claim_id=claim.id,
                        source_version_id=svid,
                        evidence_excerpt=e.get("excerpt"),
                        locator=e.get("locator"),
                        retrieved_at=_parse_iso(e.get("captured_at")),
                        evidence_strength=e.get("strength") or "WEAK",
                    )
                )

            report.synced_claims += 1
            await self._audit(
                "sync_claim",
                "claim",
                str(claim.id),
                {"research_claim_key": research_key, "pipeline_status": status},
            )

        # Gaps from conflicts
        conflicts_path = staging / "conflicts.json"
        if conflicts_path.exists() and not self.dry_run:
            conflicts = json.loads(conflicts_path.read_text(encoding="utf-8")).get(
                "conflicts", []
            )
            for conf in conflicts:
                catalogue_id = conf.get("service_id")
                service = await self.resolve_runtime_service(catalogue_id, mappings, report)
                if not service:
                    continue
                self.session.add(
                    KnowledgeGap(
                        service_id=service.id,
                        gap_type=KnowledgeGapType.CONFLICTING_SOURCES.value,
                        priority=KnowledgeGapPriority.HIGH.value,
                        description=conf.get("topic") or conf.get("resolution") or "Conflict",
                        discovered_by="batch_research_sync",
                        status=KnowledgeGapStatus.OPEN.value,
                        resolution_notes=json.dumps(conf, ensure_ascii=False)[:2000],
                    )
                )

        if not self.dry_run:
            await self.session.flush()
        return report

    async def publish_verified(self, batch_id: str) -> PublishReport:
        """Publish only gate-eligible VERIFIED OFFICIAL claims into Fee/Checklist/Steps."""
        report = PublishReport(dry_run=self.dry_run, batch_id=batch_id)
        mappings = await self.load_mappings()
        staging = self.staging_dir(batch_id)
        # Operate on DB claims for mapped services in this batch
        services_meta = json.loads((staging / "services.json").read_text(encoding="utf-8"))[
            "services"
        ]
        catalogue_ids = [s["service_id"] for s in services_meta]

        for catalogue_id in catalogue_ids:
            mapping = mappings.get(catalogue_id)
            if not mapping:
                continue
            service = await self.resolve_runtime_service(catalogue_id, mappings, report)
            if not service:
                continue

            result = await self.session.execute(
                select(Claim)
                .where(Claim.service_id == service.id)
                .options(selectinload(Claim.evidence_links))
            )
            claims = list(result.scalars().all())

            # Conflict gate: if any CONFLICTING fee/document claims, mark service
            conflicting = [
                c for c in claims if c.pipeline_status == ClaimPipelineStatus.CONFLICTING.value
            ]
            if conflicting and not self.dry_run:
                service.status = "CONFLICTED"
                service.review_state = "PENDING_REVIEW"

            for claim in claims:
                if claim.pipeline_status != ClaimPipelineStatus.VERIFIED.value:
                    report.skipped += 1
                    report.actions.append(
                        {
                            "action": "skip_unverified",
                            "claim_id": str(claim.id),
                            "status": claim.pipeline_status,
                        }
                    )
                    continue

                tiers, evidence_dicts, provenance_ok, hash_ok, retrieved = await self._claim_context(
                    claim
                )
                has_conflict = any(
                    c.pipeline_status == ClaimPipelineStatus.CONFLICTING.value
                    and c.claim_type == claim.claim_type
                    for c in claims
                    if c.id != claim.id
                )
                gate = evaluate_official_publication(
                    pipeline_status=claim.pipeline_status,
                    information_class=claim.information_class,
                    claim_type=claim.claim_type,
                    evidence=evidence_dicts,
                    authority_tiers=tiers,
                    has_unresolved_conflict=has_conflict,
                    verified_at=claim.verified_at,
                    reviewer_approved=claim.verified_at is not None,
                    provenance_complete=provenance_ok,
                    content_hash_present=hash_ok,
                    retrieved_at=retrieved,
                )
                if not gate.allowed:
                    report.skipped += 1
                    report.actions.append(
                        {
                            "action": "reject_gate",
                            "claim_id": str(claim.id),
                            "reasons": gate.reasons,
                        }
                    )
                    continue

                # MVP seed overwrite protection for structured fields
                if service.slug in MVP_SEED_SLUGS and not mapping.get("allow_overwrite_seed"):
                    report.errors.append(
                        f"Refusing to overwrite MVP seed {service.slug} from claim {claim.id}; "
                        "set allow_overwrite_seed after review"
                    )
                    continue

                if claim.claim_type == ClaimType.FEE.value:
                    fee_gate = can_populate_fee(
                        gate=gate,
                        information_class=claim.information_class,
                        claim_type=claim.claim_type,
                    )
                    if not fee_gate.allowed:
                        report.skipped += 1
                        continue
                    await self._publish_fee(service, claim, report)
                elif claim.claim_type in {
                    ClaimType.DOCUMENT.value,
                    ClaimType.CONDITIONAL_DOCUMENT.value,
                }:
                    must_gate = can_populate_must_need(
                        information_class=claim.information_class,
                        pipeline_status=claim.pipeline_status,
                        gate=gate,
                    )
                    if not must_gate.allowed:
                        report.skipped += 1
                        continue
                    await self._publish_checklist(service, claim, report)
                elif claim.claim_type == ClaimType.PROCEDURE_STEP.value:
                    step_gate = can_populate_procedure_step(
                        gate=gate, information_class=claim.information_class
                    )
                    if not step_gate.allowed:
                        report.skipped += 1
                        continue
                    await self._publish_step(service, claim, report)
                else:
                    # Mark claim published for non-structural types without inventing fields
                    if not self.dry_run:
                        claim.is_published = True
                        claim.published_at = datetime.now(timezone.utc)
                    report.actions.append(
                        {
                            "action": "mark_claim_published_metadata_only",
                            "claim_id": str(claim.id),
                            "claim_type": claim.claim_type,
                        }
                    )

        if report.errors:
            if not self.dry_run:
                await self.session.rollback()
            raise ValidationError("Publication validation failed: " + "; ".join(report.errors))

        if not self.dry_run:
            await self.session.flush()
        return report

    async def _claim_context(
        self, claim: Claim
    ) -> tuple[list[int], list[dict], bool, bool | None, datetime | None]:
        tiers: list[int] = []
        evidence_dicts: list[dict] = []
        provenance_ok = True
        hash_present = False
        retrieved: datetime | None = None
        for ev in claim.evidence_links:
            evidence_dicts.append(
                {
                    "evidence_excerpt": ev.evidence_excerpt,
                    "locator": ev.locator,
                    "knowledge_chunk_id": str(ev.knowledge_chunk_id)
                    if ev.knowledge_chunk_id
                    else None,
                }
            )
            if not ev.source_version_id:
                provenance_ok = False
                continue
            sv = await self.session.get(SourceVersion, ev.source_version_id)
            if not sv:
                provenance_ok = False
                continue
            if sv.content_hash:
                hash_present = True
            if sv.retrieved_at or sv.fetched_at:
                retrieved = sv.retrieved_at or sv.fetched_at
            src = await self.session.get(Source, sv.source_id)
            if src:
                tiers.append(int(src.tier))
            else:
                provenance_ok = False
        return tiers, evidence_dicts, provenance_ok, (hash_present if evidence_dicts else None), retrieved

    async def _publish_fee(self, service: Service, claim: Claim, report: PublishReport) -> None:
        amount = None
        currency = "BDT"
        if claim.structured_value and "amount" in claim.structured_value:
            amount = str(claim.structured_value["amount"])
            currency = claim.structured_value.get("currency", "BDT")
        else:
            # Do not invent amount from prose
            report.errors.append(
                f"Fee claim {claim.id} missing structured_value.amount; refusing invent"
            )
            return
        if self.dry_run:
            report.published_fees += 1
            report.actions.append(
                {"action": "would_publish_fee", "claim_id": str(claim.id), "amount": amount}
            )
            return
        fee = Fee(
            service_id=service.id,
            label_bn=claim.subject,
            label_en=claim.subject,
            amount=amount,
            currency=currency,
            effective_date=claim.effective_from,
            claim_id=claim.id,
            verified_at=claim.verified_at,
            notes_en=f"Published from claim {claim.id}",
        )
        self.session.add(fee)
        claim.is_published = True
        claim.published_at = datetime.now(timezone.utc)
        report.published_fees += 1
        await self._audit("publish_fee", "fee", str(claim.id), {"amount": amount})

    async def _publish_checklist(
        self, service: Service, claim: Claim, report: PublishReport
    ) -> None:
        item_type = (
            "CONDITIONAL"
            if claim.claim_type == ClaimType.CONDITIONAL_DOCUMENT.value
            else "REQUIRED"
        )
        if self.dry_run:
            report.published_checklist += 1
            report.actions.append(
                {
                    "action": "would_publish_checklist",
                    "claim_id": str(claim.id),
                    "item_type": item_type,
                }
            )
            return
        item = ChecklistItem(
            service_id=service.id,
            order=0,
            item_type=item_type,
            label_bn=claim.value[:512],
            label_en=claim.value[:512],
            claim_id=claim.id,
            confidence=claim.confidence,
            conditions=(claim.structured_value or {}).get("condition"),
        )
        self.session.add(item)
        claim.is_published = True
        claim.published_at = datetime.now(timezone.utc)
        report.published_checklist += 1
        await self._audit("publish_checklist", "checklist_item", str(claim.id), {"type": item_type})

    async def _publish_step(self, service: Service, claim: Claim, report: PublishReport) -> None:
        if self.dry_run:
            report.published_steps += 1
            report.actions.append(
                {"action": "would_publish_step", "claim_id": str(claim.id)}
            )
            return
        # Attach to active procedure or create verified procedure
        result = await self.session.execute(
            select(Procedure).where(Procedure.service_id == service.id, Procedure.is_active.is_(True))
        )
        procedure = result.scalar_one_or_none()
        if not procedure:
            procedure = Procedure(
                service_id=service.id,
                key="verified-default",
                title_bn="যাচাইকৃত প্রক্রিয়া",
                title_en="Verified procedure",
            )
            self.session.add(procedure)
            await self.session.flush()
        order = (claim.structured_value or {}).get("order") or 1
        step = ProcedureStep(
            procedure_id=procedure.id,
            order=int(order),
            key=f"claim-{claim.id.hex[:8]}",
            title_bn=claim.subject[:512],
            title_en=claim.subject[:512],
            description_en=claim.value,
            claim_id=claim.id,
            last_verified_at=claim.verified_at,
            status="active",
        )
        self.session.add(step)
        claim.is_published = True
        claim.published_at = datetime.now(timezone.utc)
        report.published_steps += 1
        await self._audit("publish_step", "procedure_step", str(claim.id), {"order": order})


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _split_claim(text: str) -> tuple[str, str]:
    text = (text or "").strip()
    if not text:
        return ("unknown", "asserts")
    # naive split
    for sep in (" is ", " are ", " requires ", " must ", " = "):
        if sep in text.lower():
            idx = text.lower().index(sep)
            return text[:idx].strip()[:512] or "subject", sep.strip()
    return text[:120], "asserts"


def _map_claim_type(c: dict[str, Any]) -> str:
    explicit = c.get("claim_type")
    if explicit and explicit != "other":
        return explicit
    field = (c.get("field") or "").lower()
    text = (c.get("claim_text") or c.get("claim") or "").lower()
    if "fee" in field or "fee" in text or "bdt" in text:
        return ClaimType.FEE.value
    if "document" in field or "certificate" in text:
        return ClaimType.DOCUMENT.value
    if "url" in field or "http" in text:
        return ClaimType.APPLICATION_URL.value
    if "step" in field or "procedure" in text:
        return ClaimType.PROCEDURE_STEP.value
    return ClaimType.OTHER.value
