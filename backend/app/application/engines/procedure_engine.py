"""Structured procedure engine."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.knowledge import Service
from app.schemas.chat import ProcedureStepResponse


class ProcedureEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def build_steps(
        self,
        service: Service,
        *,
        claim_linked_only: bool = True,
    ) -> list[ProcedureStepResponse]:
        await self.session.refresh(service, ["procedures"])
        steps: list[ProcedureStepResponse] = []
        for procedure in service.procedures:
            await self.session.refresh(procedure, ["steps"])
            for step in sorted(procedure.steps, key=lambda x: x.order):
                claim_linked = step.claim_id is not None
                if claim_linked_only and not claim_linked:
                    continue
                steps.append(
                    ProcedureStepResponse(
                        order=step.order,
                        title=step.title_en,
                        official_url=step.official_url,
                        claim_linked=claim_linked,
                    )
                )
        return steps
