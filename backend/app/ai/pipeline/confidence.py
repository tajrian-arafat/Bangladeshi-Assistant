"""Confidence and answer-support calculation."""

from __future__ import annotations

from typing import Any

from app.domain.enums import AnswerSupportLevel
from app.domain.models.knowledge import Service
from app.application.knowledge.publication_gate import answer_support_for_service_claims


def calculate_confidence(
    service: Service | None,
    evidence: list[dict[str, Any]],
    conflicts: list[str],
    *,
    support_level: str | AnswerSupportLevel | None = None,
) -> str:
    if support_level is not None:
        level = (
            support_level.value
            if isinstance(support_level, AnswerSupportLevel)
            else str(support_level)
        )
        if level == AnswerSupportLevel.VERIFIED.value:
            return "high"
        if level == AnswerSupportLevel.PARTIALLY_SUPPORTED.value:
            return "medium"
        return "low"

    if not service:
        return "low"
    if conflicts:
        return "low"
    if service.status in {"CONFLICTED", "UNDER_REVIEW", "OUTDATED", "DISABLED"}:
        return "low"
    if service.status != "ACTIVE":
        return "low"
    if evidence and any(e.get("tier", 6) <= 2 for e in evidence):
        return "high" if len(evidence) >= 2 else "medium"
    if service.last_verified_at:
        return "medium"
    return "low"


def support_level_from_claim_rows(claim_rows: list[dict[str, Any]]) -> AnswerSupportLevel:
    return answer_support_for_service_claims(claim_rows)
