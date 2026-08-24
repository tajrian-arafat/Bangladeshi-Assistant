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
from app.application.knowledge.verification_sync import (
    build_fee_structured_by_claim,
    claim_type_from_verification,
    domain_from_url,
    evidence_excerpt_from_verification,
    hash_snapshot,
    load_verification_index,
    parse_verified_at,
    pipeline_status_for_claim,
    verification_dir,
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
    ServiceLink,
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
    published_urls: int = 0
    published_practical: int = 0
    synced_claims: int = 0
    skipped: int = 0
    eligible_count: int = 0
    rejected_by_gate_count: int = 0
    post_readiness: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def audit_summary(self) -> dict[str, Any]:
        """Dry-run / post-publish audit payload."""
        eligible = [a for a in self.actions if a.get("action", "").startswith(("would_publish", "mark_claim_published"))]
        rejected = [a for a in self.actions if a.get("action") == "reject_gate"]
        skipped_actions = [a for a in self.actions if a.get("action", "").startswith("skip_")]
        return {
            "eligible_for_publication": len(eligible),
            "rejected_by_gate": len(rejected),
            "skipped": self.skipped,
            "published_fees": self.published_fees,
            "published_checklist": self.published_checklist,
            "published_steps": self.published_steps,
            "published_urls": self.published_urls,
            "practical_stored": self.published_practical,
            "synced_claims": self.synced_claims,
            "errors": self.errors,
            "rejected_samples": rejected[:15],
            "eligible_samples": eligible[:15],
            "skipped_samples": skipped_actions[:15],
            "post_readiness": self.post_readiness,
        }


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
        """Upsert Source/SourceVersion/Claim/Evidence/Gaps.

        Applies independent verification statuses from verification/batch-01.
        Never promotes claims to VERIFIED without a verification record.
        """
        report = PublishReport(dry_run=self.dry_run, batch_id=batch_id)
        staging = self.staging_dir(batch_id)
        sources = json.loads((staging / "sources.json").read_text(encoding="utf-8"))["sources"]
        versions = json.loads((staging / "source_versions.json").read_text(encoding="utf-8"))[
            "source_versions"
        ]
        claims = json.loads((staging / "claims.json").read_text(encoding="utf-8"))["claims"]
        evidence = json.loads((staging / "evidence.json").read_text(encoding="utf-8"))["evidence"]
        mappings = await self.load_mappings()
        verification_index = load_verification_index(self.repo_root, batch_id)
        fee_structured = build_fee_structured_by_claim(staging)
        vdir = verification_dir(self.repo_root, batch_id)

        if not verification_index:
            report.errors.append(
                f"No independent verification index found for {batch_id}; "
                "run verify_batch01_claims.py before publication"
            )
            return report

        # Block staging-only VERIFIED without matching verification record
        for c in claims:
            if c.get("pipeline_status") == ClaimPipelineStatus.VERIFIED.value:
                v = verification_index.get(c.get("claim_id"))
                if not v or v.get("verification_status") != "VERIFIED":
                    report.errors.append(
                        f"Staging claim {c.get('claim_id')} has VERIFIED status without "
                        "independent verification; demote before sync."
                    )
        if report.errors:
            return report

        source_id_map: dict[str, UUID] = {}
        version_id_map: dict[str, UUID] = {}
        url_to_version_id: dict[str, UUID] = {}

        for s in sources:
            domain = s.get("domain") or urlparse(s.get("source_url", "")).netloc
            existing = await self.session.execute(
                select(Source).where(Source.domain == domain, Source.title == s.get("source_title"))
            )
            row = existing.scalar_one_or_none()
            if not row:
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
            source_id_map[s["source_id"]] = row.id

        # Index verification snapshots by source_url for hash enrichment
        snapshot_hash_by_url: dict[str, str] = {}
        for vrec in verification_index.values():
            for ev in vrec.get("evidence", []):
                url = ev.get("source_url") or ev.get("wayback_url")
                snap = ev.get("snapshot")
                if url and snap:
                    h = hash_snapshot(self.repo_root, snap)
                    if h:
                        snapshot_hash_by_url[url] = h

        for v in versions:
            sid = source_id_map.get(v["source_id"])
            if not sid:
                continue
            content_hash = v.get("content_hash") or snapshot_hash_by_url.get(v.get("url"))
            raw_pointer = v.get("raw_pointer")
            if not content_hash and vdir:
                # Try verification snapshot via source_id
                for vrec in verification_index.values():
                    for ev in vrec.get("evidence", []):
                        if ev.get("source_id") == v.get("source_id") and ev.get("snapshot"):
                            content_hash = hash_snapshot(self.repo_root, ev["snapshot"])
                            raw_pointer = raw_pointer or ev["snapshot"]
                            break
            if self.dry_run:
                vid = uuid4()
                version_id_map[v["source_version_id"]] = vid
                url_to_version_id[v["url"]] = vid
                report.actions.append(
                    {
                        "action": "would_create_source_version",
                        "url": v.get("url"),
                        "content_hash": content_hash,
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
                    content_hash=content_hash,
                    retrieved_at=_parse_iso(v.get("retrieved_at")),
                    fetched_at=_parse_iso(v.get("retrieved_at")),
                    retrieval_method=v.get("fetched_method") or v.get("retrieval_method"),
                    http_status=v.get("http_status"),
                    title=None,
                    raw_content_path=raw_pointer,
                    metadata_json={"research_source_version_id": v["source_version_id"]},
                )
                self.session.add(row)
                await self.session.flush()
            elif content_hash and not row.content_hash:
                row.content_hash = content_hash
                if raw_pointer and not row.raw_content_path:
                    row.raw_content_path = raw_pointer
            version_id_map[v["source_version_id"]] = row.id
            url_to_version_id[v["url"]] = row.id

        evidence_by_claim: dict[str, list[dict]] = {}
        for e in evidence:
            evidence_by_claim.setdefault(e["claim_id"], []).append(e)

        for c in claims:
            catalogue_id = c.get("service_id")
            if not catalogue_id:
                continue
            service = await self.resolve_runtime_service(catalogue_id, mappings, report)
            if not service:
                continue

            research_key = c["claim_id"]
            verification = verification_index.get(research_key)
            status = pipeline_status_for_claim(c, verification)
            claim_type = claim_type_from_verification(c, verification)
            info_class = (
                (verification or {}).get("information_class")
                or c.get("information_class")
                or InformationClass.DISCOVERY.value
            )
            verified_at = None
            if status == ClaimPipelineStatus.VERIFIED.value and verification:
                verified_at = parse_verified_at(verification.get("verified_at"))

            fee_rows = fee_structured.get(research_key, [])
            structured_value = None
            if fee_rows:
                structured_value = fee_rows[0] if len(fee_rows) == 1 else {"fee_tiers": fee_rows}
            elif verification and verification.get("condition"):
                structured_value = {
                    "condition": verification["condition"],
                    "applicability": verification.get("applicability"),
                }

            if self.dry_run:
                report.synced_claims += 1
                report.actions.append(
                    {
                        "action": "would_upsert_claim",
                        "research_claim_key": research_key,
                        "pipeline_status": status,
                        "claim_type": claim_type,
                        "information_class": info_class,
                        "runtime_slug": service.slug,
                        "verification_status": (verification or {}).get("verification_status"),
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
                    claim_type=claim_type,
                    subject=subject,
                    predicate=predicate,
                    value=c.get("claim_text") or c.get("claim") or "",
                    structured_value=structured_value,
                    information_class=info_class,
                    pipeline_status=status,
                    confidence=c.get("confidence"),
                    verified_at=verified_at,
                    review_notes=(verification or {}).get("reasoning"),
                )
                self.session.add(claim)
                await self.session.flush()
            else:
                claim.pipeline_status = status
                claim.claim_type = claim_type
                claim.confidence = c.get("confidence")
                claim.value = c.get("claim_text") or claim.value
                claim.information_class = info_class
                claim.structured_value = structured_value or claim.structured_value
                claim.verified_at = verified_at
                if verification:
                    claim.review_notes = verification.get("reasoning")

            # Staging evidence links
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
                ev_row = existing_ev.scalar_one_or_none()
                if ev_row:
                    if not ev_row.evidence_excerpt and e.get("excerpt"):
                        ev_row.evidence_excerpt = e.get("excerpt")
                    continue
                self.session.add(
                    ClaimEvidence(
                        claim_id=claim.id,
                        source_version_id=svid,
                        evidence_excerpt=e.get("excerpt"),
                        locator=e.get("locator"),
                        retrieved_at=_parse_iso(e.get("captured_at")),
                        evidence_strength=e.get("strength") or "WEAK",
                        verified_at=verified_at,
                    )
                )

            # Verification evidence (primary for gate)
            if verification:
                for ev in verification.get("evidence", []):
                    url = ev.get("source_url") or ev.get("wayback_url")
                    if not url:
                        continue
                    svid = url_to_version_id.get(url)
                    if not svid and not self.dry_run:
                        domain = domain_from_url(url)
                        src_existing = await self.session.execute(
                            select(Source).where(Source.domain == domain).limit(1)
                        )
                        src_row = src_existing.scalar_one_or_none()
                        if not src_row:
                            src_row = Source(
                                domain=domain,
                                title=ev.get("source_id") or domain,
                                tier=int(ev.get("authority_tier") or 6),
                            )
                            self.session.add(src_row)
                            await self.session.flush()
                        snap = ev.get("snapshot")
                        ch = hash_snapshot(self.repo_root, snap) if snap else None
                        sv_existing = await self.session.execute(
                            select(SourceVersion).where(
                                SourceVersion.source_id == src_row.id,
                                SourceVersion.url == url,
                            )
                        )
                        sv_row = sv_existing.scalar_one_or_none()
                        if not sv_row:
                            sv_row = SourceVersion(
                                source_id=src_row.id,
                                url=url,
                                canonical_url=url,
                                content_hash=ch,
                                retrieved_at=parse_verified_at(ev.get("retrieved_live_at")),
                                fetched_at=parse_verified_at(ev.get("retrieved_live_at")),
                                retrieval_method=ev.get("retrieved_via") or "independent_verification",
                                http_status=ev.get("live_http_status"),
                                raw_content_path=snap,
                                metadata_json={"verification_source_id": ev.get("source_id")},
                            )
                            self.session.add(sv_row)
                            await self.session.flush()
                        elif ch and not sv_row.content_hash:
                            sv_row.content_hash = ch
                        svid = sv_row.id
                        url_to_version_id[url] = svid

                    if not svid:
                        continue
                    excerpt = evidence_excerpt_from_verification(ev, verification)
                    locator = ev.get("evidence_location") or url
                    existing_ev = await self.session.execute(
                        select(ClaimEvidence).where(
                            ClaimEvidence.claim_id == claim.id,
                            ClaimEvidence.source_version_id == svid,
                        )
                    )
                    ev_row = existing_ev.scalar_one_or_none()
                    if ev_row:
                        if not ev_row.evidence_excerpt:
                            ev_row.evidence_excerpt = excerpt
                        if not ev_row.locator:
                            ev_row.locator = locator
                        if verified_at and not ev_row.verified_at:
                            ev_row.verified_at = verified_at
                        ev_row.evidence_strength = "STRONG"
                        continue
                    self.session.add(
                        ClaimEvidence(
                            claim_id=claim.id,
                            source_version_id=svid,
                            evidence_excerpt=excerpt,
                            locator=locator,
                            retrieved_at=parse_verified_at(
                                ev.get("retrieved_live_at") or verification.get("verified_at")
                            ),
                            evidence_strength="STRONG",
                            verified_at=verified_at,
                        )
                    )

            report.synced_claims += 1
            await self._audit(
                "sync_claim",
                "claim",
                str(claim.id),
                {
                    "research_claim_key": research_key,
                    "pipeline_status": status,
                    "verification_status": (verification or {}).get("verification_status"),
                },
            )

        # Knowledge gaps from verification
        gaps_path = (
            verification_dir(self.repo_root, batch_id) or Path()
        ) / "knowledge_gaps.json"
        if gaps_path.exists() and not self.dry_run:
            gap_data = json.loads(gaps_path.read_text(encoding="utf-8"))
            gaps = gap_data.get("knowledge_gaps") or gap_data.get("gaps") or []
            for gap in gaps:
                catalogue_id = gap.get("service_id")
                if not catalogue_id and gap.get("related_claims"):
                    rc = gap["related_claims"][0]
                    catalogue_id = rc.split("::")[0] if "::" in rc else None
                service = await self.resolve_runtime_service(catalogue_id, mappings, report)
                if not service:
                    continue
                gap_type_raw = gap.get("gap_type") or gap.get("gap_id") or KnowledgeGapType.OTHER.value
                gap_type = gap_type_raw.lower() if isinstance(gap_type_raw, str) else KnowledgeGapType.OTHER.value
                if gap_type.startswith("missing_"):
                    pass
                elif gap_type.startswith("MISSING_"):
                    gap_type = gap_type.lower()
                existing_gap = await self.session.execute(
                    select(KnowledgeGap).where(
                        KnowledgeGap.service_id == service.id,
                        KnowledgeGap.description == (gap.get("notes") or gap.get("gap_id") or "")[:500],
                    ).limit(1)
                )
                if existing_gap.scalar_one_or_none():
                    continue
                self.session.add(
                    KnowledgeGap(
                        service_id=service.id,
                        gap_type=gap_type if gap_type in {e.value for e in KnowledgeGapType} else KnowledgeGapType.OTHER.value,
                        priority=gap.get("priority") or KnowledgeGapPriority.MEDIUM.value,
                        description=gap.get("notes") or gap.get("gap_id") or gap.get("description") or "Gap",
                        discovered_by="batch01_verification",
                        status=KnowledgeGapStatus.OPEN.value,
                        resolution_notes=json.dumps(gap, ensure_ascii=False)[:2000],
                    )
                )

        if not self.dry_run:
            await self.session.flush()
        return report

    async def publish_verified(
        self,
        batch_id: str,
        *,
        approved_seed_replacement_claim_ids: set[UUID] | None = None,
    ) -> PublishReport:
        """Publish only gate-eligible VERIFIED OFFICIAL claims into Fee/Checklist/Steps/URLs."""
        report = PublishReport(dry_run=self.dry_run, batch_id=batch_id)
        approved_replacements = approved_seed_replacement_claim_ids or set()
        mappings = await self.load_mappings()
        staging = self.staging_dir(batch_id)
        fee_structured = build_fee_structured_by_claim(staging)
        services_meta = json.loads((staging / "services.json").read_text(encoding="utf-8"))[
            "services"
        ]
        catalogue_ids = [s["service_id"] for s in services_meta]
        verification_index = load_verification_index(self.repo_root, batch_id)
        processed_service_ids: set[UUID] = set()

        for catalogue_id in catalogue_ids:
            mapping = mappings.get(catalogue_id)
            if not mapping:
                continue
            service = await self.resolve_runtime_service(catalogue_id, mappings, report)
            if not service:
                continue
            if service.id in processed_service_ids:
                continue
            processed_service_ids.add(service.id)

            result = await self.session.execute(
                select(Claim)
                .where(Claim.service_id == service.id)
                .options(selectinload(Claim.evidence_links))
            )
            claims = list(result.scalars().all())

            conflicting = [
                c for c in claims if c.pipeline_status == ClaimPipelineStatus.CONFLICTING.value
            ]
            if conflicting and not self.dry_run:
                service.status = "CONFLICTED"
                service.review_state = "PENDING_REVIEW"

            published_official = 0
            critical_gaps = 0

            for claim in claims:
                vrec = verification_index.get(claim.research_claim_key or "")
                vstatus = (vrec or {}).get("verification_status")

                # PRACTICAL layer — store non-authoritative tips; never MUST NEED / fees
                if claim.information_class == InformationClass.PRACTICAL.value:
                    if claim.pipeline_status not in {
                        ClaimPipelineStatus.VERIFIED.value,
                        ClaimPipelineStatus.PARTIALLY_VERIFIED.value,
                    }:
                        report.skipped += 1
                        report.actions.append(
                            {
                                "action": "skip_practical_unverified",
                                "claim_id": str(claim.id),
                                "research_claim_key": claim.research_claim_key,
                                "status": claim.pipeline_status,
                            }
                        )
                        continue
                    if not self.dry_run:
                        claim.is_published = True
                        claim.published_at = datetime.now(timezone.utc)
                    report.published_practical += 1
                    report.actions.append(
                        {
                            "action": "would_publish_practical"
                            if self.dry_run
                            else "publish_practical",
                            "claim_id": str(claim.id),
                            "research_claim_key": claim.research_claim_key,
                            "pipeline_status": claim.pipeline_status,
                        }
                    )
                    continue

                # Never publish non-VERIFIED official claims as authoritative
                if claim.pipeline_status != ClaimPipelineStatus.VERIFIED.value:
                    report.skipped += 1
                    report.actions.append(
                        {
                            "action": "skip_unverified",
                            "claim_id": str(claim.id),
                            "research_claim_key": claim.research_claim_key,
                            "status": claim.pipeline_status,
                            "verification_status": vstatus,
                        }
                    )
                    continue

                # Block news/static NID fee amounts explicitly
                if claim.research_claim_key and "fee-amount-news" in claim.research_claim_key:
                    report.skipped += 1
                    report.actions.append(
                        {
                            "action": "skip_unresolved_fee_amount",
                            "claim_id": str(claim.id),
                            "research_claim_key": claim.research_claim_key,
                            "reason": "Unresolved NID static fee amounts must not publish",
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
                    report.rejected_by_gate_count += 1
                    report.actions.append(
                        {
                            "action": "reject_gate",
                            "claim_id": str(claim.id),
                            "research_claim_key": claim.research_claim_key,
                            "claim_type": claim.claim_type,
                            "reasons": gate.reasons,
                        }
                    )
                    if claim.claim_type in {
                        ClaimType.FEE.value,
                        ClaimType.DOCUMENT.value,
                        ClaimType.APPLICATION_URL.value,
                    }:
                        critical_gaps += 1
                    continue

                report.eligible_count += 1
                seed_block_structured = (
                    service.slug in MVP_SEED_SLUGS
                    and not mapping.get("allow_overwrite_seed")
                    and claim.id not in approved_replacements
                )

                if claim.claim_type == ClaimType.FEE.value:
                    fee_gate = can_populate_fee(
                        gate=gate,
                        information_class=claim.information_class,
                        claim_type=claim.claim_type,
                    )
                    if not fee_gate.allowed:
                        report.skipped += 1
                        continue
                    if seed_block_structured:
                        report.actions.append(
                            {
                                "action": "skip_mvp_seed_fee_overwrite",
                                "claim_id": str(claim.id),
                                "service_slug": service.slug,
                            }
                        )
                        report.skipped += 1
                        continue
                    fee_rows = fee_structured.get(claim.research_claim_key or "", [])
                    if not fee_rows and claim.structured_value:
                        if claim.structured_value.get("fee_tiers"):
                            fee_rows = claim.structured_value["fee_tiers"]
                        else:
                            fee_rows = [claim.structured_value]
                    if not fee_rows:
                        report.actions.append(
                            {
                                "action": "skip_fee_no_structured_value",
                                "claim_id": str(claim.id),
                            }
                        )
                        report.skipped += 1
                        continue
                    for fee_payload in fee_rows:
                        await self._publish_fee(service, claim, report, fee_payload)
                    published_official += 1
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
                    if seed_block_structured:
                        report.actions.append(
                            {
                                "action": "skip_mvp_seed_checklist_overwrite",
                                "claim_id": str(claim.id),
                                "service_slug": service.slug,
                            }
                        )
                        report.skipped += 1
                        continue
                    await self._publish_checklist(service, claim, report, vrec)
                    published_official += 1
                elif claim.claim_type == ClaimType.PROCEDURE_STEP.value:
                    step_gate = can_populate_procedure_step(
                        gate=gate, information_class=claim.information_class
                    )
                    if not step_gate.allowed:
                        report.skipped += 1
                        continue
                    if seed_block_structured:
                        report.actions.append(
                            {
                                "action": "skip_mvp_seed_step_overwrite",
                                "claim_id": str(claim.id),
                                "service_slug": service.slug,
                            }
                        )
                        report.skipped += 1
                        continue
                    await self._publish_step(service, claim, report)
                    published_official += 1
                elif claim.claim_type == ClaimType.APPLICATION_URL.value:
                    await self._publish_application_url(service, claim, report, vrec)
                    published_official += 1
                else:
                    if not self.dry_run:
                        claim.is_published = True
                        claim.published_at = datetime.now(timezone.utc)
                    report.actions.append(
                        {
                            "action": "mark_claim_published_metadata_only",
                            "claim_id": str(claim.id),
                            "claim_type": claim.claim_type,
                            "research_claim_key": claim.research_claim_key,
                        }
                    )
                    published_official += 1

            report.post_readiness[catalogue_id] = self._compute_readiness(
                claims=claims,
                published_official=published_official,
                critical_gaps=critical_gaps,
            )
            if not self.dry_run:
                readiness = report.post_readiness[catalogue_id]
                if readiness == "GREEN":
                    service.status = "ACTIVE"
                    service.review_state = "APPROVED"
                elif readiness == "YELLOW":
                    service.status = "UNDER_REVIEW"
                    service.review_state = "PENDING_REVIEW"
                elif readiness == "RED":
                    # Incomplete coverage — not the same as material claim CONFLICT
                    service.status = "UNDER_REVIEW"
                    service.review_state = "PENDING_REVIEW"

        if report.errors:
            if not self.dry_run:
                await self.session.rollback()
            raise ValidationError("Publication validation failed: " + "; ".join(report.errors))

        if not self.dry_run:
            await self.session.flush()
        return report

    def _compute_readiness(
        self,
        *,
        claims: list[Claim],
        published_official: int,
        critical_gaps: int,
    ) -> str:
        """Post-publication readiness from published claim coverage."""
        if critical_gaps > 0:
            return "RED"
        verified = [
            c
            for c in claims
            if c.pipeline_status == ClaimPipelineStatus.VERIFIED.value
            and c.information_class == InformationClass.OFFICIAL.value
        ]
        if not verified:
            return "RED"
        published = [c for c in verified if c.is_published]
        if len(published) >= len(verified) and published_official > 0:
            return "GREEN"
        if published_official > 0:
            return "YELLOW"
        return "RED"

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

    async def _publish_fee(
        self,
        service: Service,
        claim: Claim,
        report: PublishReport,
        fee_payload: dict[str, Any] | None = None,
    ) -> None:
        payload = fee_payload or claim.structured_value or {}
        currency = payload.get("currency", "BDT")
        label = payload.get("description") or claim.subject or claim.value[:120]

        if payload.get("fee_mode") == "calculator" or (
            payload.get("amount") is None and payload.get("fee_mode") != "fixed"
        ):
            amount = "USE_OFFICIAL_CALCULATOR"
            calc_url = payload.get("calculator_url") or "https://services.nidw.gov.bd/nid-pub/fees"
            notes_en = (
                f"Official fee must be calculated via the portal calculator: {calc_url}. "
                f"Published from claim {claim.research_claim_key}."
            )
        elif payload.get("amount") is not None:
            amount = str(payload["amount"])
            notes_en = f"Published from claim {claim.research_claim_key}"
            calc_url = None
        else:
            report.errors.append(
                f"Fee claim {claim.id} missing structured amount/calculator; refusing invent"
            )
            return

        if self.dry_run:
            report.published_fees += 1
            report.actions.append(
                {
                    "action": "would_publish_fee",
                    "claim_id": str(claim.id),
                    "research_claim_key": claim.research_claim_key,
                    "amount": amount,
                    "calculator_url": calc_url,
                    "condition": payload.get("condition"),
                }
            )
            return
        fee = Fee(
            service_id=service.id,
            label_bn=label[:512],
            label_en=label[:512],
            amount=amount,
            currency=currency,
            effective_date=claim.effective_from,
            claim_id=claim.id,
            verified_at=claim.verified_at,
            notes_en=notes_en,
        )
        self.session.add(fee)
        claim.is_published = True
        claim.published_at = datetime.now(timezone.utc)
        report.published_fees += 1
        await self._audit(
            "publish_fee",
            "fee",
            str(claim.id),
            {"amount": amount, "calculator_url": calc_url},
        )

    async def _publish_checklist(
        self,
        service: Service,
        claim: Claim,
        report: PublishReport,
        verification: dict[str, Any] | None = None,
    ) -> None:
        item_type = (
            "CONDITIONAL"
            if claim.claim_type == ClaimType.CONDITIONAL_DOCUMENT.value
            else "REQUIRED"
        )
        conditions = (claim.structured_value or {}).get("condition")
        if verification and verification.get("condition"):
            conditions = verification["condition"]
        if self.dry_run:
            report.published_checklist += 1
            report.actions.append(
                {
                    "action": "would_publish_checklist",
                    "claim_id": str(claim.id),
                    "research_claim_key": claim.research_claim_key,
                    "item_type": item_type,
                    "condition": conditions,
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
            conditions=conditions,
        )
        self.session.add(item)
        claim.is_published = True
        claim.published_at = datetime.now(timezone.utc)
        report.published_checklist += 1
        await self._audit(
            "publish_checklist",
            "checklist_item",
            str(claim.id),
            {"type": item_type, "condition": conditions},
        )

    async def _publish_application_url(
        self,
        service: Service,
        claim: Claim,
        report: PublishReport,
        verification: dict[str, Any] | None = None,
    ) -> None:
        url = None
        if verification:
            for ev in verification.get("evidence", []):
                if ev.get("source_url"):
                    url = ev["source_url"]
                    break
        if not url:
            text = claim.value
            for token in text.split():
                if token.startswith("http"):
                    url = token.rstrip(".,)")
                    break
        if not url:
            report.actions.append(
                {
                    "action": "skip_url_missing",
                    "claim_id": str(claim.id),
                    "research_claim_key": claim.research_claim_key,
                }
            )
            return
        if self.dry_run:
            report.published_urls += 1
            report.actions.append(
                {
                    "action": "would_publish_url",
                    "claim_id": str(claim.id),
                    "research_claim_key": claim.research_claim_key,
                    "url": url,
                }
            )
            return
        existing = await self.session.execute(
            select(ServiceLink).where(ServiceLink.service_id == service.id, ServiceLink.url == url)
        )
        if not existing.scalar_one_or_none():
            self.session.add(
                ServiceLink(
                    service_id=service.id,
                    link_type="APPLICATION",
                    label_bn=claim.subject[:512] or "আবেদন পোর্টাল",
                    label_en=claim.subject[:512] or "Application portal",
                    url=url,
                    is_verified=True,
                    last_checked_at=claim.verified_at,
                )
            )
        claim.is_published = True
        claim.published_at = datetime.now(timezone.utc)
        report.published_urls += 1
        await self._audit("publish_url", "service_link", str(claim.id), {"url": url})

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
