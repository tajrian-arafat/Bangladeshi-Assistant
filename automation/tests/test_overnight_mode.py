"""Overnight mode and policy engine tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from automation.orchestrator.policy_engine import EscalationPolicy, PolicyEngine
from automation.orchestrator.phase_runner import PhaseRunner
from automation.orchestrator.state_machine import StateMachine
from automation.schemas.result import PhaseResult
from automation.schemas.state import ProjectState, WorkflowStatus


REPO = Path(__file__).resolve().parents[2]
STATE_PATH = REPO / ".automation" / "project_state.json"


@pytest.fixture()
def isolated_state():
    backup = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else None
    yield
    if backup is not None:
        STATE_PATH.write_text(backup, encoding="utf-8")


def test_policy_defers_local_regression() -> None:
    engine = PolicyEngine()
    decision = engine.evaluate_phase_outcome(
        phase="REGRESSION",
        result={"summary": "Regression: 1 failures", "status": "BLOCKED", "regressions": 1},
        workflow_status="SUPERVISOR_REVIEW",
        retry_count=0,
    )
    assert decision.policy == EscalationPolicy.AUTO_DEFER_AND_CONTINUE
    assert decision.continue_workflow is True


def test_policy_blocks_hallucination_after_retries() -> None:
    engine = PolicyEngine()
    decision = engine.evaluate_phase_outcome(
        phase="E2E",
        result={"summary": "hallucination", "hallucinations": 1, "status": "BLOCKED"},
        workflow_status="BLOCKED",
        retry_count=3,
    )
    assert decision.policy == EscalationPolicy.BLOCKED_GLOBAL
    assert decision.continue_workflow is False


def test_supervisor_review_regression_resumes(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = ProjectState(
        current_batch="BATCH_03C",
        current_phase="REGRESSION",
        current_run_id="run-overnight-test",
        workflow_status=WorkflowStatus.SUPERVISOR_REVIEW.value,
        retry_count=2,
        pending_escalations=[],
        idempotency_keys=["BATCH_03C:REGRESSION:complete"],
    )

    def fake_execute(_s: ProjectState, _b: dict) -> PhaseResult:
        return PhaseResult.empty_success(
            run_id="run-overnight-test-regression",
            batch_id="BATCH_03C",
            phase="REGRESSION",
            summary="All regression suites passed",
            recommended_next_phase="",
        )

    monkeypatch.setattr(runner, "execute_current_phase", fake_execute)
    StateMachine(REPO).save(state)
    report = runner.run_autonomous_step(state)
    loaded = StateMachine(REPO).load()
    assert report["result_status"] == "SUCCESS"
    assert loaded.workflow_status in {
        WorkflowStatus.COMPLETE.value,
        WorkflowStatus.READY.value,
        WorkflowStatus.AUTO_CONTINUE.value,
    }
