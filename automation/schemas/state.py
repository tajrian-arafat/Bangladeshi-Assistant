"""Workflow and project state models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class WorkflowStatus(StrEnum):
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING_FOR_RESULT = "WAITING_FOR_RESULT"
    VALIDATING_RESULT = "VALIDATING_RESULT"
    AUTO_CONTINUE = "AUTO_CONTINUE"
    RETRY = "RETRY"
    GAP_CLOSURE = "GAP_CLOSURE"
    SUPERVISOR_REVIEW = "SUPERVISOR_REVIEW"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


class WorkflowPhase(StrEnum):
    RESEARCH = "RESEARCH"
    VERIFICATION = "VERIFICATION"
    GAP_CLOSURE = "GAP_CLOSURE"
    PUBLICATION = "PUBLICATION"
    E2E = "E2E"
    REGRESSION = "REGRESSION"
    STABILIZATION = "STABILIZATION"


# Allowed transitions: current -> set(next)
ALLOWED_TRANSITIONS: dict[WorkflowStatus, frozenset[WorkflowStatus]] = {
    WorkflowStatus.READY: frozenset({WorkflowStatus.RUNNING}),
    WorkflowStatus.RUNNING: frozenset({WorkflowStatus.WAITING_FOR_RESULT}),
    WorkflowStatus.WAITING_FOR_RESULT: frozenset({WorkflowStatus.VALIDATING_RESULT}),
    WorkflowStatus.VALIDATING_RESULT: frozenset(
        {
            WorkflowStatus.AUTO_CONTINUE,
            WorkflowStatus.RETRY,
            WorkflowStatus.GAP_CLOSURE,
            WorkflowStatus.SUPERVISOR_REVIEW,
            WorkflowStatus.HUMAN_APPROVAL_REQUIRED,
            WorkflowStatus.BLOCKED,
            WorkflowStatus.COMPLETE,
        }
    ),
    WorkflowStatus.AUTO_CONTINUE: frozenset({WorkflowStatus.RUNNING, WorkflowStatus.COMPLETE}),
    WorkflowStatus.RETRY: frozenset({WorkflowStatus.RUNNING}),
    WorkflowStatus.GAP_CLOSURE: frozenset({WorkflowStatus.RUNNING}),
    WorkflowStatus.SUPERVISOR_REVIEW: frozenset(
        {WorkflowStatus.HUMAN_APPROVAL_REQUIRED, WorkflowStatus.RUNNING, WorkflowStatus.BLOCKED}
    ),
    WorkflowStatus.HUMAN_APPROVAL_REQUIRED: frozenset(
        {WorkflowStatus.RUNNING, WorkflowStatus.BLOCKED, WorkflowStatus.STOPPED}
    ),
    WorkflowStatus.BLOCKED: frozenset(
        {WorkflowStatus.HUMAN_APPROVAL_REQUIRED, WorkflowStatus.STOPPED, WorkflowStatus.READY, WorkflowStatus.RETRY}
    ),
    WorkflowStatus.COMPLETE: frozenset({WorkflowStatus.READY}),
    WorkflowStatus.PAUSED: frozenset({WorkflowStatus.RUNNING, WorkflowStatus.STOPPED}),
    WorkflowStatus.STOPPED: frozenset({WorkflowStatus.READY}),
}


PHASE_ORDER: list[WorkflowPhase] = [
    WorkflowPhase.RESEARCH,
    WorkflowPhase.VERIFICATION,
    WorkflowPhase.GAP_CLOSURE,
    WorkflowPhase.PUBLICATION,
    WorkflowPhase.E2E,
    WorkflowPhase.REGRESSION,
    WorkflowPhase.STABILIZATION,
]


def assert_transition(current: WorkflowStatus, nxt: WorkflowStatus) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current, frozenset())
    if nxt not in allowed:
        raise ValueError(f"Illegal workflow transition: {current.value} -> {nxt.value}")


@dataclass
class RegressionBaseline:
    batch_01_e2e: str = "55/55"
    passport_e2e_pct: float = 100.0
    batch_02b_e2e_pct: float = 100.0
    routing_benchmark_pct: float = 100.0
    pytest_count: int = 58
    hallucinations: int = 0
    citation_failures: int = 0


@dataclass
class CatalogueStats:
    canonical_services: int = 464
    confirmed_services: int = 454
    unverified_services: int = 10


@dataclass
class ProjectState:
    project_name: str = "Bangladeshi Assistant"
    mode: str = "LOCAL_DEV_ONLY"
    deployment_allowed: bool = False
    current_batch: str | None = "BATCH_03A"
    current_phase: str | None = WorkflowPhase.RESEARCH.value
    current_run_id: str | None = None
    workflow_status: str = WorkflowStatus.READY.value
    last_completed_batch: str = "BATCH_02B"
    catalogue: CatalogueStats = field(default_factory=CatalogueStats)
    regression_baseline: RegressionBaseline = field(default_factory=RegressionBaseline)
    pending_escalations: list[str] = field(default_factory=list)
    pilot_mode: bool = True
    continuous_mode: bool = False
    simulation_mode: bool = False
    retry_count: int = 0
    idempotency_keys: list[str] = field(default_factory=list)
    updated_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectState:
        catalogue = data.get("catalogue") or {}
        regression = data.get("regression_baseline") or {}
        return cls(
            project_name=data.get("project_name", "Bangladeshi Assistant"),
            mode=data.get("mode", "LOCAL_DEV_ONLY"),
            deployment_allowed=bool(data.get("deployment_allowed", False)),
            current_batch=data.get("current_batch"),
            current_phase=data.get("current_phase"),
            current_run_id=data.get("current_run_id"),
            workflow_status=data.get("workflow_status", WorkflowStatus.READY.value),
            last_completed_batch=data.get("last_completed_batch", "BATCH_02B"),
            catalogue=CatalogueStats(**catalogue) if isinstance(catalogue, dict) else CatalogueStats(),
            regression_baseline=(
                RegressionBaseline(**regression) if isinstance(regression, dict) else RegressionBaseline()
            ),
            pending_escalations=list(data.get("pending_escalations") or []),
            pilot_mode=bool(data.get("pilot_mode", True)),
            continuous_mode=bool(data.get("continuous_mode", False)),
            simulation_mode=bool(data.get("simulation_mode", False)),
            retry_count=int(data.get("retry_count", 0)),
            idempotency_keys=list(data.get("idempotency_keys") or []),
            updated_at=data.get("updated_at"),
            metadata=dict(data.get("metadata") or {}),
        )
