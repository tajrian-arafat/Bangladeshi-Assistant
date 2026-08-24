"""Intent-aware structured claim retrieval."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.routing.intent_classifier import IntentResult
from app.ai.routing.loader import intent_claim_types
from app.domain.enums import ClaimPipelineStatus, InformationClass
from app.domain.models.claims import Claim
from app.domain.models.knowledge import Fee, Service


class ClaimRetrieval:
    """Retrieve published claims filtered by intent and claim type."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def claim_types_for_intents(self, intents: IntentResult) -> list[str]:
        types: list[str] = []
        seen: set[str] = set()
        for intent in intents.all_intents:
            for ct in intent_claim_types(intent):
                if ct not in seen:
                    seen.add(ct)
                    types.append(ct)
        return types

    async def published_claims(
        self,
        service_id: Any,
        intents: IntentResult,
        *,
        limit: int = 50,
    ) -> list[Claim]:
        claim_types = self.claim_types_for_intents(intents)
        if not claim_types:
            return []

        query = (
            select(Claim)
            .where(
                Claim.service_id == service_id,
                Claim.is_published.is_(True),
                Claim.information_class == InformationClass.OFFICIAL.value,
                Claim.pipeline_status == ClaimPipelineStatus.VERIFIED.value,
                Claim.claim_type.in_(claim_types),
            )
            .options(selectinload(Claim.evidence_links))
            .limit(limit)
        )
        return list((await self.session.execute(query)).scalars().all())

    async def fees_for_intent(
        self,
        service: Service,
        intents: IntentResult,
    ) -> list[Fee]:
        await self.session.refresh(service, ["fees"])
        if intents.primary not in {"fee_inquiry", "payment", "renewal", "reissue"} and "fee_inquiry" not in intents.secondary:
            return []

        fee_claim_ids = {
            c.id
            for c in await self.published_claims(service.id, IntentResult(primary="fee_inquiry"))
        }
        if not fee_claim_ids:
            # No published fee claims — return nothing (orchestrator adds warning)
            return []

        return [fee for fee in service.fees if fee.claim_id in fee_claim_ids]

    async def has_claim_coverage(
        self,
        service_id: Any,
        intents: IntentResult,
    ) -> bool:
        claims = await self.published_claims(service_id, intents)
        return len(claims) > 0

    async def practical_notes(
        self,
        service_id: Any,
        *,
        limit: int = 10,
    ) -> list[str]:
        if not service_id:
            return []
        result = await self.session.execute(
            select(Claim)
            .where(
                Claim.service_id == service_id,
                Claim.information_class == InformationClass.PRACTICAL.value,
                Claim.is_published.is_(True),
            )
            .limit(limit)
        )
        return [
            f"[PRACTICAL — not official MUST NEED] {claim.value}"
            for claim in result.scalars().all()
        ]
