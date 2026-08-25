"""Conflict detection across evidence."""

from __future__ import annotations

from typing import Any


def detect_conflicts(evidence: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    fees = {e.get("fee_amount") for e in evidence if e.get("fee_amount")}
    if len(fees) > 1:
        warnings.append("Fee information conflicts between sources.")
    doc_sets = [frozenset(e.get("documents") or []) for e in evidence if e.get("documents")]
    if len(doc_sets) > 1 and len(set(doc_sets)) > 1:
        warnings.append("Required document lists differ between sources.")
    return warnings
