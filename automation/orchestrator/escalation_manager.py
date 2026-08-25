"""Human escalation and decision management."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from automation.schemas.decision import DecisionRecord
from automation.schemas.escalation import EscalationRecord


class EscalationManager:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.decisions_dir = repo_root / ".automation" / "decisions"
        self.decisions_dir.mkdir(parents=True, exist_ok=True)

    def create_decision(
        self,
        *,
        batch: str,
        issue: str,
        severity: str,
        evidence: list[dict] | None = None,
        recommended_action: str = "",
        publication_blocked: bool = True,
        simulation: bool = False,
        status: str = "HUMAN_APPROVAL_REQUIRED",
    ) -> DecisionRecord:
        prefix = "sim" if simulation else "dec"
        decision_id = f"{prefix}-{uuid.uuid4().hex[:12]}"
        record = DecisionRecord(
            decision_id=decision_id,
            status=status,
            batch=batch,
            issue=issue,
            severity=severity,
            evidence=evidence or [],
            recommended_action=recommended_action,
            publication_blocked=publication_blocked,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        path = self.decisions_dir / f"{decision_id}.json"
        payload = record.to_dict()
        if simulation:
            payload["simulation"] = True
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return record

    def defer_for_human_review(
        self,
        *,
        batch: str,
        issue: str,
        severity: str = "MEDIUM",
        evidence: list[dict] | None = None,
        recommended_action: str = "Review when available — overnight run continued",
    ) -> DecisionRecord:
        """Record deferred human review without blocking the autonomous catalogue run."""
        return self.create_decision(
            batch=batch,
            issue=issue,
            severity=severity,
            evidence=evidence,
            recommended_action=recommended_action,
            publication_blocked=True,
            status="DEFERRED_HUMAN_REVIEW",
        )

    def load_decision(self, decision_id: str) -> DecisionRecord:
        path = self.decisions_dir / f"{decision_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        return DecisionRecord.from_dict(data)

    def resolve_decision(self, decision_id: str, *, resolution: str, approved_by: str) -> DecisionRecord:
        record = self.load_decision(decision_id)
        record.status = "RESOLVED"
        record.resolution = resolution
        record.approved_by = approved_by
        record.resolved_at = datetime.now(timezone.utc).isoformat()
        path = self.decisions_dir / f"{decision_id}.json"
        path.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")
        return record

    def list_pending(self) -> list[DecisionRecord]:
        pending: list[DecisionRecord] = []
        for path in sorted(self.decisions_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("simulation"):
                continue
            record = DecisionRecord.from_dict(data)
            if record.status == "HUMAN_APPROVAL_REQUIRED":
                pending.append(record)
        return pending

    def to_escalation(self, record: DecisionRecord, *, phase: str, run_id: str | None = None) -> EscalationRecord:
        return EscalationRecord(
            escalation_id=record.decision_id,
            status=record.status,
            batch_id=record.batch,
            phase=phase,
            issue=record.issue,
            severity=record.severity,
            evidence=record.evidence,
            recommended_action=record.recommended_action,
            publication_blocked=record.publication_blocked,
            created_at=record.created_at,
            run_id=run_id,
        )
