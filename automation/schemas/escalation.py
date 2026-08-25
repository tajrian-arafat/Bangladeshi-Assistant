"""Escalation records for supervisor / human review."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EscalationRecord:
    escalation_id: str
    status: str
    batch_id: str
    phase: str
    issue: str
    severity: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    recommended_action: str = ""
    publication_blocked: bool = True
    created_at: str = ""
    run_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EscalationRecord:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
