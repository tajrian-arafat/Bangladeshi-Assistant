"""Claim review actions with audit logging."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError, ValidationError
from app.domain.enums import (
    AnswerSupportLevel,
    ClaimPipelineStatus,
    InformationClass,
)
from app.domain.models.claims import Claim, ClaimEvidence, KnowledgeGap
from app.domain.models.knowledge import Source, SourceVersion
from app.domain.models.operations import AuditLog
from app.application.knowledge.publication_gate import (
    answer_support_for_service_claims,
    evaluate_official_publication,
)


class ClaimReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _audit(
        self,
        *,
        action: str,
        resource_type: str,
        resource_id: str,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
        admin_user_id: UUID | None = None,
    ) -> None:
        self.session.add(
            AuditLog(
                admin_user_id=admin_user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                before_json=before,
                after_json=after,
            )
        )

    async def get_claim(self, claim_id: UUID) -> Claim:
        result = await self.session.execute(
            select(Claim)
            .where(Claim.id == claim_id)
            .options(selectinload(Claim.evidence_links))
        )
        claim = result.scalar_one_or_none()
        if not claim:
            raise NotFoundError("Claim", str(claim_id))
        return claim

    async def list_claims(
        self,
        *,
        service_id: UUID | None = None,
        pipeline_status: str | None = None,
        limit: int = 50,
    ) -> list[Claim]:
        stmt = select(Claim).options(selectinload(Claim.evidence_links)).limit(limit)
        if service_id:
            stmt = stmt.where(Claim.service_id == service_id)
        if pipeline_status:
            stmt = stmt.where(Claim.pipeline_status == pipeline_status)
        result = await self.session.execute(stmt.order_by(Claim.updated_at.desc()))
        return list(result.scalars().all())

    async def inspect_provenance(self, claim_id: UUID) -> dict[str, Any]:
        claim = await self.get_claim(claim_id)
        evidence_rows = []
        for ev in claim.evidence_links:
            sv = None
            source = None
            if ev.source_version_id:
                sv_result = await self.session.execute(
                    select(SourceVersion)
                    .where(SourceVersion.id == ev.source_version_id)
                    .options(selectinload(SourceVersion.source))
                )
                sv = sv_result.scalar_one_or_none()
                if sv:
                    source = sv.source
            evidence_rows.append(
                {
                    "evidence_id": str(ev.id),
                    "excerpt": ev.evidence_excerpt,
                    "strength": ev.evidence_strength,
                    "source_version_id": str(ev.source_version_id) if ev.source_version_id else None,
                    "content_hash": sv.content_hash if sv else None,
                    "raw_content_path": sv.raw_content_path if sv else None,
                    "url": sv.url if sv else None,
                    "source_id": str(source.id) if source else None,
                    "authority_tier": source.tier if source else None,
                    "source_domain": source.domain if source else None,
                }
            )
        return {
            "claim_id": str(claim.id),
            "pipeline_status": claim.pipeline_status,
            "information_class": claim.information_class,
            "is_published": claim.is_published,
            "chain": evidence_rows,
        }

    async def approve_claim(
        self,
        claim_id: UUID,
        *,
        admin_user_id: UUID | None = None,
        notes: str | None = None,
        force: bool = False,
    ) -> Claim:
        """Mark claim VERIFIED only if publication gate passes (unless force for tests).

        force=True is for admin override after documenting residual risk — still
        does NOT auto-publish into Fee/Checklist.
        """
        claim = await self.get_claim(claim_id)
        before = {"pipeline_status": claim.pipeline_status, "verified_at": None}

        if claim.pipeline_status == ClaimPipelineStatus.CONFLICTING.value and not force:
            raise ValidationError("Cannot approve CONFLICTING claim without conflict resolution")

        provenance = await self.inspect_provenance(claim_id)
        tiers = [e["authority_tier"] for e in provenance["chain"] if e.get("authority_tier") is not None]
        evidence = [
            {
                "evidence_excerpt": e.get("excerpt"),
                "locator": None,
                "knowledge_chunk_id": None,
            }
            for e in provenance["chain"]
        ]
        gate = evaluate_official_publication(
            pipeline_status=ClaimPipelineStatus.VERIFIED.value,  # evaluating target state
            information_class=claim.information_class,
            claim_type=claim.claim_type,
            evidence=evidence,
            authority_tiers=tiers,
            has_unresolved_conflict=False,
            verified_at=datetime.now(timezone.utc),
            reviewer_approved=True,
            provenance_complete=bool(provenance["chain"])
            and all(e.get("source_version_id") for e in provenance["chain"]),
            content_hash_present=any(e.get("content_hash") for e in provenance["chain"]) or None,
            retrieved_at=None,
        )
        if claim.information_class == InformationClass.OFFICIAL.value and not gate.allowed and not force:
            raise ValidationError(
                "Claim does not meet official verification gate: " + "; ".join(gate.reasons)
            )

        claim.pipeline_status = ClaimPipelineStatus.VERIFIED.value
        claim.verified_at = datetime.now(timezone.utc)
        claim.verified_by_admin_id = admin_user_id
        if notes:
            claim.review_notes = notes
        await self._audit(
            action="approve",
            resource_type="claim",
            resource_id=str(claim.id),
            before=before,
            after={
                "pipeline_status": claim.pipeline_status,
                "verified_at": claim.verified_at.isoformat(),
                "gate_reasons_if_forced": gate.reasons if force and not gate.allowed else [],
            },
            admin_user_id=admin_user_id,
        )
        await self.session.flush()
        return claim

    async def reject_claim(
        self,
        claim_id: UUID,
        *,
        admin_user_id: UUID | None = None,
        notes: str | None = None,
    ) -> Claim:
        claim = await self.get_claim(claim_id)
        before = {"pipeline_status": claim.pipeline_status}
        claim.pipeline_status = ClaimPipelineStatus.REJECTED.value
        claim.is_published = False
        claim.review_notes = notes
        await self._audit(
            action="reject",
            resource_type="claim",
            resource_id=str(claim.id),
            before=before,
            after={"pipeline_status": claim.pipeline_status, "notes": notes},
            admin_user_id=admin_user_id,
        )
        await self.session.flush()
        return claim

    async def mark_conflict(
        self,
        claim_id: UUID,
        *,
        admin_user_id: UUID | None = None,
        notes: str | None = None,
    ) -> Claim:
        claim = await self.get_claim(claim_id)
        before = {"pipeline_status": claim.pipeline_status, "is_published": claim.is_published}
        claim.pipeline_status = ClaimPipelineStatus.CONFLICTING.value
        claim.is_published = False
        claim.review_notes = notes
        await self._audit(
            action="mark_conflict",
            resource_type="claim",
            resource_id=str(claim.id),
            before=before,
            after={"pipeline_status": claim.pipeline_status},
            admin_user_id=admin_user_id,
        )
        await self.session.flush()
        return claim

    async def request_more_evidence(
        self,
        claim_id: UUID,
        *,
        admin_user_id: UUID | None = None,
        notes: str | None = None,
    ) -> Claim:
        claim = await self.get_claim(claim_id)
        before = {"pipeline_status": claim.pipeline_status}
        claim.pipeline_status = ClaimPipelineStatus.PENDING_REVIEW.value
        claim.review_notes = notes or claim.review_notes
        await self._audit(
            action="request_more_evidence",
            resource_type="claim",
            resource_id=str(claim.id),
            before=before,
            after={"pipeline_status": claim.pipeline_status, "notes": notes},
            admin_user_id=admin_user_id,
        )
        await self.session.flush()
        return claim

    async def mark_outdated(
        self,
        claim_id: UUID,
        *,
        admin_user_id: UUID | None = None,
        notes: str | None = None,
    ) -> Claim:
        claim = await self.get_claim(claim_id)
        before = {"pipeline_status": claim.pipeline_status, "is_published": claim.is_published}
        claim.pipeline_status = ClaimPipelineStatus.OUTDATED.value
        claim.is_published = False
        claim.review_notes = notes
        await self._audit(
            action="mark_outdated",
            resource_type="claim",
            resource_id=str(claim.id),
            before=before,
            after={"pipeline_status": claim.pipeline_status},
            admin_user_id=admin_user_id,
        )
        await self.session.flush()
        return claim

    async def list_gaps(self, *, service_id: UUID | None = None, limit: int = 50) -> list[KnowledgeGap]:
        stmt = select(KnowledgeGap).limit(limit)
        if service_id:
            stmt = stmt.where(KnowledgeGap.service_id == service_id)
        result = await self.session.execute(stmt.order_by(KnowledgeGap.created_at.desc()))
        return list(result.scalars().all())

    async def service_answer_support(self, service_id: UUID) -> AnswerSupportLevel:
        result = await self.session.execute(select(Claim).where(Claim.service_id == service_id))
        claims = [
            {
                "pipeline_status": c.pipeline_status,
                "information_class": c.information_class,
                "is_published": c.is_published,
            }
            for c in result.scalars().all()
        ]
        return answer_support_for_service_claims(claims)
