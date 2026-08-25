"""Escalation tests."""

from __future__ import annotations

from pathlib import Path

from automation.orchestrator.escalation_manager import EscalationManager


REPO = Path(__file__).resolve().parents[2]


def test_create_and_resolve_decision(tmp_path: Path) -> None:
    # Use repo .automation/decisions
    mgr = EscalationManager(REPO)
    record = mgr.create_decision(
        batch="TEST",
        issue="Conflicting fees",
        severity="CRITICAL",
    )
    assert record.status == "HUMAN_APPROVAL_REQUIRED"
    resolved = mgr.resolve_decision(record.decision_id, resolution="reviewed", approved_by="test")
    assert resolved.status == "RESOLVED"
