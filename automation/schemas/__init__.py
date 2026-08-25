"""Automation workflow schemas."""

from automation.schemas.decision import DecisionRecord
from automation.schemas.escalation import EscalationRecord
from automation.schemas.result import PhaseResult, validate_phase_result
from automation.schemas.state import ProjectState, WorkflowStatus, WorkflowPhase

__all__ = [
    "DecisionRecord",
    "EscalationRecord",
    "PhaseResult",
    "ProjectState",
    "WorkflowPhase",
    "WorkflowStatus",
    "validate_phase_result",
]
