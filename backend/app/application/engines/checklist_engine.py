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


class ChecklistEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def build(self, service: Service, answers: dict[str, Any]) -> list[ChecklistResult]:
        await self.session.refresh(service, ["checklist_items"])
        results: list[ChecklistResult] = []
        for item in sorted(service.checklist_items, key=lambda x: x.order):
            if item.conditions and not self._conditions_match(item.conditions, answers):
                continue
            label = item.label_bn if answers.get("_lang") == "bn" else item.label_en
            results.append(
                ChecklistResult(
                    label=label,
                    item_type=item.item_type,
                    evidence_id=str(item.evidence_chunk_id) if item.evidence_chunk_id else None,
                )
            )
        return results

    def _conditions_match(self, conditions: dict[str, Any], answers: dict[str, Any]) -> bool:
        return all(answers.get(k) == v for k, v in conditions.items())
