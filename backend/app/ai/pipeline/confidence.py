"""Confidence calculation."""

from __future__ import annotations

from typing import Any

from app.domain.models.knowledge import Service


def calculate_confidence(
    service: Service | None,
    evidence: list[dict[str, Any]],
    conflicts: list[str],
) -> str:
    if not service:
        return "low"
    if conflicts:
        return "low"
    if service.status != "ACTIVE":
        return "low"
    if evidence and any(e.get("tier", 6) <= 2 for e in evidence):
        return "high" if len(evidence) >= 2 else "medium"
    if service.last_verified_at:
        return "medium"
    return "low"
