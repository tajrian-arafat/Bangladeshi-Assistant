"""Autonomous phase continuation tests (A–J)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.phase_completion import check_research_complete
from automation.orchestrator.phase_runner import PhaseRunner
from automation.orchestrator.state_machine import StateMachine
from automation.schemas.result import PhaseResult
from automation.schemas.state import ProjectState, WorkflowPhase, WorkflowStatus


REPO = Path(__file__).resolve().parents[2]
STATE_PATH = REPO / ".automation" / "project_state.json"


@pytest.fixture()
def isolated_state(monkeypatch: pytest.MonkeyPatch):
    backup = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else None
    queue_path = REPO / ".automation" / "batch_queue.json"
    queue_backup = queue_path.read_text(encoding="utf-8") if queue_path.exists() else None
    yield
    if backup is not None:
        STATE_PATH.write_text(backup, encoding="utf-8")
    if queue_backup is not None:
        queue_path.write_text(queue_backup, encoding="utf-8")


def _state(**kwargs) -> ProjectState:
    base = ProjectState(
        current_batch="BATCH_03A",
        current_phase=WorkflowPhase.RESEARCH.value,
        current_run_id="run-test123",
        workflow_status=WorkflowStatus.READY.value,
        retry_count=0,
        pending_escalations=[],
        idempotency_keys=[],
    )
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


def test_research_completion_requires_full_artifacts() -> None:
    bm = BatchManager(REPO)
    batch = bm.get_batch("BATCH_03A")
    assert batch is not None
    report = check_research_complete(REPO, batch)
    assert report.complete, f"Batch 3A research should be complete: {report.missing}"


def test_a_research_success_auto_continue(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = _state(workflow_status=WorkflowStatus.READY.value, current_phase="RESEARCH")
    result = PhaseResult.empty_success(
        run_id="run-test123-research",
        batch_id="BATCH_03A",
        phase="RESEARCH",
        summary="ok",
        recommended_next_phase="VERIFICATION",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    StateMachine(REPO).save(state)
    report = runner.run_autonomous_step(state)
    loaded = StateMachine(REPO).load()
    assert report["result_status"] == "SUCCESS"
    assert loaded.workflow_status == WorkflowStatus.AUTO_CONTINUE.value
    assert loaded.current_phase == "VERIFICATION"


def test_b_verification_passes_to_publication(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = _state(workflow_status=WorkflowStatus.READY.value, current_phase="VERIFICATION")
    result = PhaseResult.empty_success(
        run_id="run-test123-verification",
        batch_id="BATCH_03A",
        phase="VERIFICATION",
        summary="verified",
        recommended_next_phase="PUBLICATION",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    StateMachine(REPO).save(state)
    runner.run_autonomous_step(state)
    loaded = StateMachine(REPO).load()
    assert loaded.current_phase == "PUBLICATION"
    assert loaded.workflow_status == WorkflowStatus.AUTO_CONTINUE.value


def test_c_publication_to_e2e(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = _state(workflow_status=WorkflowStatus.AUTO_CONTINUE.value, current_phase="PUBLICATION")
    result = PhaseResult.empty_success(
        run_id="run-test123-publication",
        batch_id="BATCH_03A",
        phase="PUBLICATION",
        summary="published locally",
        recommended_next_phase="E2E",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    StateMachine(REPO).save(state)
    runner.run_autonomous_step(state)
    assert StateMachine(REPO).load().current_phase == "E2E"


def test_d_e2e_to_regression(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = _state(workflow_status=WorkflowStatus.AUTO_CONTINUE.value, current_phase="E2E")
    result = PhaseResult.empty_success(
        run_id="run-test123-e2e",
        batch_id="BATCH_03A",
        phase="E2E",
        summary="e2e ok",
        recommended_next_phase="REGRESSION",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    StateMachine(REPO).save(state)
    runner.run_autonomous_step(state)
    assert StateMachine(REPO).load().current_phase == "REGRESSION"


def test_e2_continuous_regression_skips_stabilization(
    isolated_state, monkeypatch: pytest.MonkeyPatch
) -> None:
    """In continuous mode, REGRESSION success completes batch (STABILIZATION skipped)."""
    runner = PhaseRunner(REPO)
    state = _state(
        workflow_status=WorkflowStatus.AUTO_CONTINUE.value,
        current_phase="REGRESSION",
        continuous_mode=True,
    )
    result = PhaseResult.empty_success(
        run_id="run-test123-regression",
        batch_id="BATCH_03A",
        phase="REGRESSION",
        summary="regression ok",
        recommended_next_phase="STABILIZATION",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    bm = BatchManager(REPO)
    bm.mark_batch_status("BATCH_03B", "PLANNED")
    monkeypatch.setattr(
        runner.batch_manager,
        "next_pending_batch",
        lambda after=None: bm.get_batch("BATCH_03B"),
    )
    StateMachine(REPO).save(state)
    runner.run_autonomous_step(state)
    loaded = StateMachine(REPO).load()
    assert loaded.last_completed_batch == "BATCH_03A"
    assert loaded.current_batch == "BATCH_03B"
    assert loaded.current_phase == "RESEARCH"
    assert loaded.workflow_status == WorkflowStatus.READY.value


def test_e_regression_completes_batch(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = _state(workflow_status=WorkflowStatus.AUTO_CONTINUE.value, current_phase="REGRESSION")
    result = PhaseResult.empty_success(
        run_id="run-test123-regression",
        batch_id="BATCH_03A",
        phase="REGRESSION",
        summary="regression ok",
        recommended_next_phase="STABILIZATION",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    StateMachine(REPO).save(state)
    runner.run_autonomous_step(state)
    loaded = StateMachine(REPO).load()
    assert loaded.workflow_status == WorkflowStatus.AUTO_CONTINUE.value
    assert loaded.current_phase == "STABILIZATION"


def test_e2_regression_success_without_next_phase_completes_batch(
    isolated_state, monkeypatch: pytest.MonkeyPatch
) -> None:
    """REGRESSION with empty recommended_next_phase marks batch COMPLETE (skips STABILIZATION)."""
    runner = PhaseRunner(REPO)
    state = _state(
        workflow_status=WorkflowStatus.AUTO_CONTINUE.value,
        current_phase="REGRESSION",
        current_run_id="run-batch-complete",
    )
    result = PhaseResult.empty_success(
        run_id="run-batch-complete-regression",
        batch_id="BATCH_03A",
        phase="REGRESSION",
        summary="All regression suites passed",
        recommended_next_phase="",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    monkeypatch.setattr(runner.batch_manager, "next_pending_batch", lambda _after=None: None)
    StateMachine(REPO).save(state)
    runner.run_autonomous_step(state)
    loaded = StateMachine(REPO).load()
    assert loaded.workflow_status == WorkflowStatus.COMPLETE.value
    assert loaded.last_completed_batch == "BATCH_03A"
    assert BatchManager(REPO).get_batch("BATCH_03A")["status"] == "COMPLETE"


def test_f_critical_conflict_pauses(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = _state(workflow_status=WorkflowStatus.READY.value, current_phase="VERIFICATION")
    result = PhaseResult(
        run_id="run-test123-verification",
        batch_id="BATCH_03A",
        phase="VERIFICATION",
        status="ESCALATED",
        started_at="2026-08-24T00:00:00+00:00",
        completed_at="2026-08-24T00:00:01+00:00",
        critical_conflicts=1,
        requires_escalation=True,
        summary="Critical fee conflict",
        recommended_next_phase="HUMAN_APPROVAL_REQUIRED",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    StateMachine(REPO).save(state)
    report = runner.run_autonomous_step(state)
    assert report["status"] == WorkflowStatus.HUMAN_APPROVAL_REQUIRED.value


def test_g_failed_run_retries(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = _state(workflow_status=WorkflowStatus.READY.value, current_phase="E2E", retry_count=0)
    result = PhaseResult(
        run_id="run-test123-e2e",
        batch_id="BATCH_03A",
        phase="E2E",
        status="FAILED",
        started_at="2026-08-24T00:00:00+00:00",
        completed_at="2026-08-24T00:00:01+00:00",
        summary="network timeout during cursor execution",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    StateMachine(REPO).save(state)
    report = runner.run_autonomous_step(state)
    assert report["status"] == WorkflowStatus.RETRY.value


def test_h_three_retries_escalates(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = _state(workflow_status=WorkflowStatus.RETRY.value, current_phase="E2E", retry_count=3)
    result = PhaseResult(
        run_id="run-test123-e2e",
        batch_id="BATCH_03A",
        phase="E2E",
        status="FAILED",
        started_at="2026-08-24T00:00:00+00:00",
        completed_at="2026-08-24T00:00:01+00:00",
        summary="still failing",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    StateMachine(REPO).save(state)
    report = runner.run_autonomous_step(state)
    assert report["status"] == WorkflowStatus.HUMAN_APPROVAL_REQUIRED.value


def test_blocked_e2e_resumes_on_run(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    """BLOCKED at E2E should auto-resume to READY when run is invoked after fixes."""
    runner = PhaseRunner(REPO)
    state = _state(workflow_status=WorkflowStatus.BLOCKED.value, current_phase="E2E", retry_count=3)
    result = PhaseResult(
        run_id="run-test123-e2e",
        batch_id="BATCH_03B",
        phase="E2E",
        status="SUCCESS",
        started_at="2026-08-24T00:00:00+00:00",
        completed_at="2026-08-24T00:00:01+00:00",
        e2e_total=55,
        e2e_passed=55,
        hallucinations=0,
        citation_failures=0,
        summary="E2E: 55/55 passed",
        recommended_next_phase="REGRESSION",
    )
    monkeypatch.setattr(runner, "execute_current_phase", lambda s, b: result)
    StateMachine(REPO).save(state)
    report = runner.run_autonomous_step(state)
    assert report["result_status"] == "SUCCESS"
    assert report["next_phase"] == "REGRESSION"


def test_i_daemon_resumes_from_state(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    state = _state(
        workflow_status=WorkflowStatus.AUTO_CONTINUE.value,
        current_phase="VERIFICATION",
        current_run_id="run-2f560e76b418",
    )
    StateMachine(REPO).save(state)
    calls: list[str] = []

    def fake_execute(s: ProjectState, b: dict) -> PhaseResult:
        calls.append(s.current_phase or "")
        return PhaseResult.empty_success(
            run_id="run-2f560e76b418-verification",
            batch_id="BATCH_03A",
            phase="VERIFICATION",
            summary="resumed",
            recommended_next_phase="PUBLICATION",
        )

    monkeypatch.setattr(runner, "execute_current_phase", fake_execute)
    runner.run_autonomous_step(state)
    assert calls == ["VERIFICATION"]


def test_j_completed_phase_idempotent(isolated_state) -> None:
    runner = PhaseRunner(REPO)
    bm = BatchManager(REPO)
    state = _state(
        workflow_status=WorkflowStatus.AUTO_CONTINUE.value,
        current_phase="RESEARCH",
        idempotency_keys=["BATCH_03A:RESEARCH:complete"],
    )
    StateMachine(REPO).save(state)
    batch = bm.get_batch("BATCH_03A")
    assert batch is not None
    result = runner.executor.execute_research(
        run_id="run-test123-research",
        batch=batch,
        batch_manager=bm,
    )
    assert result.status == "SUCCESS"
    assert result.recommended_next_phase == "VERIFICATION"


def test_autonomous_loop_chains_phases(isolated_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = PhaseRunner(REPO)
    phases_run: list[str] = []

    def fake_execute(s: ProjectState, b: dict) -> PhaseResult:
        phase = s.current_phase or "RESEARCH"
        phases_run.append(phase)
        nxt = {"RESEARCH": "VERIFICATION", "VERIFICATION": "PUBLICATION", "PUBLICATION": "E2E"}.get(phase, "")
        return PhaseResult.empty_success(
            run_id=f"run-test-{phase.lower()}",
            batch_id="BATCH_03A",
            phase=phase,
            summary=f"{phase} ok",
            recommended_next_phase=nxt,
        )

    monkeypatch.setattr(runner, "execute_current_phase", fake_execute)
    state = _state(workflow_status=WorkflowStatus.READY.value, current_phase="RESEARCH")
    StateMachine(REPO).save(state)
    summary = runner.run_autonomous_loop(state, max_steps=3)
    assert summary["steps"] == 3
    assert phases_run == ["RESEARCH", "VERIFICATION", "PUBLICATION"]
