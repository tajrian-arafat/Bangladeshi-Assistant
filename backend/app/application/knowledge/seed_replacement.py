"""Controlled replacement of MVP seed structured data with verified claims."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.knowledge.publication_gate import (
    can_populate_fee,
    can_populate_must_need,
    can_populate_procedure_step,
    evaluate_official_publication,
)
from app.application.knowledge.publisher import KnowledgePublisher, MVP_SEED_SLUGS
from app.domain.enums import (
    ClaimPipelineStatus,
    ClaimType,
    InformationClass,
    SeedReplacementKind,
    SeedReplacementStatus,
)
from app.domain.models.claims import Claim, ServiceCatalogueMapping
from app.domain.models.knowledge import ChecklistItem, Fee, ProcedureStep, Service
from app.domain.models.operations import AuditLog
from app.domain.models.seed_replacement import SeedReplacement


@dataclass
class ReplacementCandidate:
    claim_id: UUID
    service_id: UUID
    service_slug: str
    catalogue_service_id: str | None
    research_claim_key: str | None
    replacement_kind: str
    gate_allowed: bool
    gate_reasons: list[str] = field(default_factory=list)
    existing_replacement_id: UUID | None = None
    existing_status: str | None = None
    before_snapshot: dict[str, Any] = field(default_factory=dict)
    after_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplacementReport:
    dry_run: bool
    candidates: list[ReplacementCandidate] = field(default_factory=list)
    approved: int = 0
    applied: int = 0
    rolled_back: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


class SeedReplacementService:
    def __init__(self, session: AsyncSession, *, repo_root, dry_run: bool = True) -> None:
        self.session = session
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.publisher = KnowledgePublisher(session, repo_root=repo_root, dry_run=dry_run)

    async def discover_candidates(self, batch_id: str = "batch-01") -> ReplacementReport:
        """Find gate-eligible verified claims blocked by MVP seed guard."""
        report = ReplacementReport(dry_run=self.dry_run)
        mappings = await self.publisher.load_mappings()
        seen_claim_ids: set[UUID] = set()

        for catalogue_id, mapping in mappings.items():
            runtime_slug = mapping.get("runtime_slug")
            if not runtime_slug or runtime_slug not in MVP_SEED_SLUGS:
                continue
            if mapping.get("allow_overwrite_seed"):
                continue

            service = await self.publisher.resolve_runtime_service(catalogue_id, mappings, None)
            if not service:
                continue

            claims = (
                await self.session.execute(
                    select(Claim)
                    .where(Claim.service_id == service.id)
                    .options(selectinload(Claim.evidence_links))
                )
            ).scalars().all()

            for claim in claims:
                if claim.id in seen_claim_ids:
                    continue
                kind = self._replacement_kind(claim)
                if not kind:
                    continue
                if claim.pipeline_status != ClaimPipelineStatus.VERIFIED.value:
                    continue
                if claim.information_class != InformationClass.OFFICIAL.value:
                    continue

                gate = await self._evaluate_gate(claim, claims)
                if not gate["allowed"]:
                    continue

                existing = await self._existing_replacement(claim.id)
                before = await self._legacy_snapshot(service, kind)
                after = {
                    "claim_id": str(claim.id),
                    "research_claim_key": claim.research_claim_key,
                    "structured_value": claim.structured_value,
                    "value": claim.value,
                }
                report.candidates.append(
                    ReplacementCandidate(
                        claim_id=claim.id,
                        service_id=service.id,
                        service_slug=service.slug,
                        catalogue_service_id=catalogue_id,
                        research_claim_key=claim.research_claim_key,
                        replacement_kind=kind,
                        gate_allowed=True,
                        gate_reasons=gate.get("reasons", []),
                        existing_replacement_id=existing.id if existing else None,
                        existing_status=existing.status if existing else None,
                        before_snapshot=before,
                        after_snapshot=after,
                    )
                )
                seen_claim_ids.add(claim.id)
        return report

    async def record_pending(self, candidates: list[ReplacementCandidate], batch_id: str) -> int:
        count = 0
        for cand in candidates:
            if cand.existing_replacement_id:
                continue
            if self.dry_run:
                count += 1
                continue
            row = SeedReplacement(
                service_id=cand.service_id,
                claim_id=cand.claim_id,
                catalogue_service_id=cand.catalogue_service_id,
                batch_id=batch_id,
                replacement_kind=cand.replacement_kind,
                status=SeedReplacementStatus.PENDING.value,
                gate_snapshot_json={"allowed": cand.gate_allowed, "reasons": cand.gate_reasons},
                before_json=cand.before_snapshot,
                after_json=cand.after_snapshot,
            )
            self.session.add(row)
            count += 1
        if not self.dry_run:
            await self.session.flush()
        return count

    async def approve(
        self,
        *,
        claim_ids: list[UUID] | None = None,
        replacement_ids: list[UUID] | None = None,
        approved_by: str = "review_script",
    ) -> int:
        stmt = select(SeedReplacement).where(
            SeedReplacement.status == SeedReplacementStatus.PENDING.value
        )
        if replacement_ids:
            stmt = stmt.where(SeedReplacement.id.in_(replacement_ids))
        if claim_ids:
            stmt = stmt.where(SeedReplacement.claim_id.in_(claim_ids))
        rows = (await self.session.execute(stmt)).scalars().all()
        now = datetime.now(timezone.utc)
        for row in rows:
            if self.dry_run:
                continue
            row.status = SeedReplacementStatus.APPROVED.value
            row.approved_by = approved_by
            row.approved_at = now
            self.session.add(
                AuditLog(
                    action="approve_seed_replacement",
                    resource_type="seed_replacement",
                    resource_id=str(row.id),
                    after_json={"claim_id": str(row.claim_id), "kind": row.replacement_kind},
                )
            )
        if not self.dry_run:
            await self.session.flush()
        return len(rows)

    async def apply_approved(self, batch_id: str = "batch-01") -> ReplacementReport:
        """Apply APPROVED replacements via publisher with explicit seed overwrite."""
        report = ReplacementReport(dry_run=self.dry_run)
        approved = (
            await self.session.execute(
                select(SeedReplacement)
                .where(SeedReplacement.status == SeedReplacementStatus.APPROVED.value)
                .options(selectinload(SeedReplacement.claim).selectinload(Claim.evidence_links))
            )
        ).scalars().all()

        if not approved:
            return report

        approved_claim_ids = {r.claim_id for r in approved}
        publish_report = await self.publisher.publish_verified(
            batch_id, approved_seed_replacement_claim_ids=approved_claim_ids
        )
        if publish_report.errors:
            report.errors.extend(publish_report.errors)
            return report

        now = datetime.now(timezone.utc)
        for row in approved:
            published = any(
                a.get("claim_id") == str(row.claim_id)
                and a.get("action", "").startswith(("publish_", "would_publish_", "mark_claim"))
                for a in publish_report.actions
            )
            skipped_seed = any(
                a.get("claim_id") == str(row.claim_id)
                and a.get("action") == "skip_mvp_seed_fee_overwrite"
                for a in publish_report.actions
            )
            if skipped_seed:
                report.skipped += 1
                report.errors.append(
                    f"Claim {row.claim_id} still blocked by seed guard after approval"
                )
                continue
            if not published and row.replacement_kind != SeedReplacementKind.FEE.value:
                published = row.claim_id in approved_claim_ids and publish_report.published_fees + publish_report.published_checklist + publish_report.published_steps > 0

            if self.dry_run:
                report.applied += 1
                continue

            row.status = SeedReplacementStatus.APPLIED.value
            row.applied_at = now
            self.session.add(
                AuditLog(
                    action="apply_seed_replacement",
                    resource_type="seed_replacement",
                    resource_id=str(row.id),
                    before_json=row.before_json,
                    after_json=row.after_json,
                )
            )
            report.applied += 1

        if not self.dry_run:
            await self.session.flush()
        return report

    async def rollback(self, replacement_id: UUID) -> bool:
        row = await self.session.get(SeedReplacement, replacement_id)
        if not row or row.status != SeedReplacementStatus.APPLIED.value:
            return False

        before = row.before_json or {}
        service = await self.session.get(Service, row.service_id)
        if not service:
            return False

        if self.dry_run:
            return True

        claim = await self.session.get(Claim, row.claim_id)
        if claim:
            claim.is_published = False
            claim.published_at = None

        if row.replacement_kind == SeedReplacementKind.FEE.value:
            await self.session.execute(
                select(Fee).where(Fee.claim_id == row.claim_id)
            )
            from sqlalchemy import delete

            await self.session.execute(delete(Fee).where(Fee.claim_id == row.claim_id))
            for legacy in before.get("fees", []):
                self.session.add(
                    Fee(
                        service_id=service.id,
                        label_bn=legacy.get("label_bn", "")[:512],
                        label_en=legacy.get("label_en", "")[:512],
                        amount=legacy.get("amount", "0"),
                        currency=legacy.get("currency", "BDT"),
                        claim_id=None,
                        notes_en=legacy.get("notes_en"),
                    )
                )
        elif row.replacement_kind == SeedReplacementKind.CHECKLIST.value:
            from sqlalchemy import delete

            await self.session.execute(
                delete(ChecklistItem).where(ChecklistItem.claim_id == row.claim_id)
            )
            for legacy in before.get("checklist", []):
                self.session.add(
                    ChecklistItem(
                        service_id=service.id,
                        label_bn=legacy.get("label_bn", "")[:512],
                        label_en=legacy.get("label_en", "")[:512],
                        item_type=legacy.get("item_type", "REQUIRED"),
                        claim_id=None,
                    )
                )
        elif row.replacement_kind == SeedReplacementKind.PROCEDURE_STEP.value:
            from sqlalchemy import delete

            await self.session.execute(
                delete(ProcedureStep).where(ProcedureStep.claim_id == row.claim_id)
            )
            for legacy in before.get("steps", []):
                self.session.add(
                    ProcedureStep(
                        procedure_id=legacy.get("procedure_id"),
                        order=legacy.get("order", 0),
                        title_bn=legacy.get("title_bn", "")[:512],
                        title_en=legacy.get("title_en", "")[:512],
                        claim_id=None,
                    )
                )

        row.status = SeedReplacementStatus.ROLLED_BACK.value
        row.rolled_back_at = datetime.now(timezone.utc)
        self.session.add(
            AuditLog(
                action="rollback_seed_replacement",
                resource_type="seed_replacement",
                resource_id=str(row.id),
                before_json=row.after_json,
                after_json=row.before_json,
            )
        )
        await self.session.flush()
        return True

    async def get_approved_claim_ids(self) -> set[UUID]:
        rows = (
            await self.session.execute(
                select(SeedReplacement.claim_id).where(
                    SeedReplacement.status == SeedReplacementStatus.APPROVED.value
                )
            )
        ).scalars().all()
        return set(rows)

    def _replacement_kind(self, claim: Claim) -> str | None:
        if claim.claim_type == ClaimType.FEE.value:
            return SeedReplacementKind.FEE.value
        if claim.claim_type in {ClaimType.DOCUMENT.value, ClaimType.CONDITIONAL_DOCUMENT.value}:
            return SeedReplacementKind.CHECKLIST.value
        if claim.claim_type == ClaimType.PROCEDURE_STEP.value:
            return SeedReplacementKind.PROCEDURE_STEP.value
        return None

    async def _evaluate_gate(self, claim: Claim, claims: list[Claim]) -> dict[str, Any]:
        tiers, evidence_dicts, provenance_ok, hash_ok, retrieved = (
            await self.publisher._claim_context(claim)
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
            return {"allowed": False, "reasons": gate.reasons}
        if claim.claim_type == ClaimType.FEE.value:
            fee_gate = can_populate_fee(
                gate=gate,
                information_class=claim.information_class,
                claim_type=claim.claim_type,
            )
            return {"allowed": fee_gate.allowed, "reasons": fee_gate.reasons}
        if claim.claim_type in {ClaimType.DOCUMENT.value, ClaimType.CONDITIONAL_DOCUMENT.value}:
            must_gate = can_populate_must_need(
                information_class=claim.information_class,
                pipeline_status=claim.pipeline_status,
                gate=gate,
            )
            return {"allowed": must_gate.allowed, "reasons": must_gate.reasons}
        if claim.claim_type == ClaimType.PROCEDURE_STEP.value:
            step_gate = can_populate_procedure_step(
                gate=gate, information_class=claim.information_class
            )
            return {"allowed": step_gate.allowed, "reasons": step_gate.reasons}
        return {"allowed": gate.allowed, "reasons": []}

    async def _existing_replacement(self, claim_id: UUID) -> SeedReplacement | None:
        result = await self.session.execute(
            select(SeedReplacement)
            .where(SeedReplacement.claim_id == claim_id)
            .order_by(SeedReplacement.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _legacy_snapshot(self, service: Service, kind: str) -> dict[str, Any]:
        snapshot: dict[str, Any] = {}
        if kind == SeedReplacementKind.FEE.value:
            fees = (
                await self.session.execute(
                    select(Fee).where(Fee.service_id == service.id, Fee.claim_id.is_(None))
                )
            ).scalars().all()
            snapshot["fees"] = [
                {
                    "label_bn": f.label_bn,
                    "label_en": f.label_en,
                    "amount": f.amount,
                    "currency": f.currency,
                    "notes_en": f.notes_en,
                }
                for f in fees
            ]
        elif kind == SeedReplacementKind.CHECKLIST.value:
            items = (
                await self.session.execute(
                    select(ChecklistItem).where(
                        ChecklistItem.service_id == service.id, ChecklistItem.claim_id.is_(None)
                    )
                )
            ).scalars().all()
            snapshot["checklist"] = [
                {
                    "label_bn": i.label_bn,
                    "label_en": i.label_en,
                    "item_type": i.item_type,
                }
                for i in items
            ]
        elif kind == SeedReplacementKind.PROCEDURE_STEP.value:
            steps = (
                await self.session.execute(
                    select(ProcedureStep).where(ProcedureStep.claim_id.is_(None))
                )
            ).scalars().all()
            snapshot["steps"] = [
                {
                    "procedure_id": str(s.procedure_id),
                    "order": s.order,
                    "title_bn": s.title_bn,
                    "title_en": s.title_en,
                }
                for s in steps
                if s.procedure_id
            ]
        return snapshot
