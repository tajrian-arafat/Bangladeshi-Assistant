"""Structured checklist engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.knowledge import Service


@dataclass
class ChecklistResult:
    label: str
    item_type: str
    evidence_id: str | None = None
    claim_linked: bool = False
    layer: str = "OFFICIAL"


class ChecklistEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def build(
        self,
        service: Service,
        answers: dict[str, Any],
        *,
        authoritative_only: bool = True,
    ) -> list[ChecklistResult]:
        await self.session.refresh(service, ["checklist_items"])
        results: list[ChecklistResult] = []
        for item in sorted(service.checklist_items, key=lambda x: x.order):
            if item.conditions and not self._conditions_match(item.conditions, answers):
                continue
            claim_linked = item.claim_id is not None
            if authoritative_only and not claim_linked:
                # MVP seed / unverified placeholders must not populate MUST NEED
                continue
            label = item.label_bn if answers.get("_lang") == "bn" else item.label_en
            results.append(
                ChecklistResult(
                    label=label,
                    item_type=item.item_type,
                    evidence_id=str(item.evidence_chunk_id) if item.evidence_chunk_id else None,
                    claim_linked=claim_linked,
                    layer="OFFICIAL",
                )
            )
        return results

    def _conditions_match(self, conditions: dict[str, Any] | str | None, answers: dict[str, Any]) -> bool:
        if not conditions:
            return True
        if isinstance(conditions, str):
            # Unstructured condition text — do not treat as satisfied
            return False
        if not isinstance(conditions, dict):
            return False
        # Nested condition objects from research (field/op/value) cannot match
        # flat clarifications — treat as unmatched rather than leaking into MUST NEED.
        if any(isinstance(v, (dict, list)) for v in conditions.values()):
            if not answers.get("_include_structured_conditions"):
                return False
        return all(answers.get(k) == v for k, v in conditions.items())
