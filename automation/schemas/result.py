"""Phase result contract — authoritative machine-readable output."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


REQUIRED_RESULT_FIELDS = frozenset(
    {
        "run_id",
        "batch_id",
        "phase",
        "status",
        "started_at",
        "completed_at",
        "services_total",
        "services_processed",
        "claims_total",
        "verified",
        "partial",
        "unverified",
        "conflicting",
        "outdated",
        "rejected",
        "critical_conflicts",
        "knowledge_gaps",
        "e2e_total",
        "e2e_passed",
        "e2e_failed",
        "hallucinations",
        "citation_failures",
        "regressions",
        "artifacts",
        "requires_escalation",
        "recommended_next_phase",
        "summary",
    }
)


ALLOWED_RESULT_STATUSES = frozenset(
    {"SUCCESS", "PARTIAL", "FAILED", "BLOCKED", "ESCALATED", "SIMULATED"}
)


@dataclass
class PhaseResult:
    run_id: str
    batch_id: str
    phase: str
    status: str
    started_at: str
    completed_at: str
    services_total: int = 0
    services_processed: int = 0
    claims_total: int = 0
    verified: int = 0
    partial: int = 0
    unverified: int = 0
    conflicting: int = 0
    outdated: int = 0
    rejected: int = 0
    critical_conflicts: int = 0
    knowledge_gaps: int = 0
    e2e_total: int = 0
    e2e_passed: int = 0
    e2e_failed: int = 0
    hallucinations: int = 0
    citation_failures: int = 0
    regressions: int = 0
    artifacts: list[str] = field(default_factory=list)
    requires_escalation: bool = False
    recommended_next_phase: str = ""
    summary: str = ""
    idempotency_key: str = ""
    simulation_case: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhaseResult:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def empty_success(
        cls,
        *,
        run_id: str,
        batch_id: str,
        phase: str,
        summary: str,
        recommended_next_phase: str = "",
    ) -> PhaseResult:
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            run_id=run_id,
            batch_id=batch_id,
            phase=phase,
            status="SUCCESS",
            started_at=now,
            completed_at=now,
            recommended_next_phase=recommended_next_phase,
            summary=summary,
            idempotency_key=f"{batch_id}:{phase}:{run_id}",
        )


def validate_phase_result(data: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    missing = REQUIRED_RESULT_FIELDS - set(data.keys())
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")
    status = data.get("status")
    if status not in ALLOWED_RESULT_STATUSES:
        errors.append(f"invalid status: {status!r}")
    for int_field in (
        "services_total",
        "services_processed",
        "claims_total",
        "verified",
        "partial",
        "unverified",
        "conflicting",
        "outdated",
        "rejected",
        "critical_conflicts",
        "knowledge_gaps",
        "e2e_total",
        "e2e_passed",
        "e2e_failed",
        "hallucinations",
        "citation_failures",
        "regressions",
    ):
        if int_field in data and not isinstance(data[int_field], int):
            errors.append(f"{int_field} must be int")
    if "artifacts" in data and not isinstance(data["artifacts"], list):
        errors.append("artifacts must be list")
    if "requires_escalation" in data and not isinstance(data["requires_escalation"], bool):
        errors.append("requires_escalation must be bool")
    return len(errors) == 0, errors
