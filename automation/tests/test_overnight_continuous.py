"""Continuous overnight loop tests — must not exit after batch completion."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.overnight_runner import OvernightRunner
from automation.orchestrator.state_machine import StateMachine
from automation.schemas.state import ProjectState, WorkflowStatus


REPO = Path(__file__).resolve().parents[2]
STATE_PATH = REPO / ".automation" / "project_state.json"
QUEUE_PATH = REPO / ".automation" / "batch_queue.json"


@pytest.fixture()
def restore_state():
    state_backup = STATE_PATH.read_text(encoding="utf-8") if STATE_PATH.exists() else None
    queue_backup = QUEUE_PATH.read_text(encoding="utf-8") if QUEUE_PATH.exists() else None
    yield
    if state_backup is not None:
        STATE_PATH.write_text(state_backup, encoding="utf-8")
    if queue_backup is not None:
        QUEUE_PATH.write_text(queue_backup, encoding="utf-8")


def test_next_pending_batch_skips_complete(restore_state) -> None:
    bm = BatchManager(REPO)
    for bid in ["BATCH_01", "BATCH_02A", "BATCH_02B", "BATCH_03A", "BATCH_03B", "BATCH_03C", "BATCH_04"]:
        bm.mark_batch_status(bid, "COMPLETE")
    bm.mark_batch_status("BATCH_05", "PLANNED")
    nxt = bm.next_pending_batch("BATCH_04")
    assert nxt is not None
    assert nxt["batch_id"] == "BATCH_05"


def test_next_pending_batch_does_not_wrap_around(restore_state) -> None:
    """After the last batch, must not revisit earlier READY batches."""
    bm = BatchManager(REPO)
    queue = bm.load_queue()
    for batch in queue["batches"]:
        bm.mark_batch_status(batch["batch_id"], "COMPLETE")
    bm.mark_batch_status("BATCH_03A", "READY")
    assert bm.next_pending_batch("BATCH_14") is None


def test_sync_completed_batches_from_idempotency(restore_state) -> None:
    bm = BatchManager(REPO)
    bm.mark_batch_status("BATCH_05", "IN_PROGRESS")
    updated = bm.sync_completed_batches(
        [
            "BATCH_05:RESEARCH:complete",
            "BATCH_05:VERIFICATION:complete",
            "BATCH_05:REGRESSION:complete",
        ]
    )
    assert "BATCH_05" in updated
    assert bm.get_batch("BATCH_05")["status"] == "COMPLETE"


def test_run_until_terminal_continues_after_batch_complete(restore_state, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = OvernightRunner(REPO)
    bm = BatchManager(REPO)

    bm.mark_batch_status("BATCH_SIM_A", "IN_PROGRESS")
    bm.mark_batch_status("BATCH_SIM_B", "PLANNED")

    # Ensure SIM batches exist in queue for next_pending_batch
    queue = bm.load_queue()
    if not any(b["batch_id"] == "BATCH_SIM_A" for b in queue["batches"]):
        queue["batches"].extend(
            [
                {"batch_id": "BATCH_SIM_A", "slug": "batch-sim-a", "status": "IN_PROGRESS", "service_ids": ["s1"], "service_count": 1},
                {"batch_id": "BATCH_SIM_B", "slug": "batch-sim-b", "status": "PLANNED", "service_ids": ["s2"], "service_count": 1},
            ]
        )
        bm.queue_path.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")

    state = ProjectState(
        current_batch="BATCH_SIM_A",
        current_phase="REGRESSION",
        current_run_id="run-sim-a",
        workflow_status=WorkflowStatus.READY.value,
        last_completed_batch="BATCH_04",
        pending_escalations=[],
        idempotency_keys=[],
    )
    StateMachine(REPO).save(state)

    calls: list[str] = []

    def fake_step(_state: ProjectState) -> dict:
        loaded = StateMachine(REPO).load()
        calls.append(f"{loaded.current_batch}:{loaded.current_phase}:{loaded.workflow_status}")
        if len(calls) == 1:
            bm.mark_batch_status("BATCH_SIM_A", "COMPLETE")
            loaded.current_batch = "BATCH_SIM_B"
            loaded.current_phase = "RESEARCH"
            loaded.workflow_status = WorkflowStatus.READY.value
            loaded.last_completed_batch = "BATCH_SIM_A"
            StateMachine(REPO).save(loaded)
            return {
                "status": WorkflowStatus.READY.value,
                "batch": "BATCH_SIM_B",
                "phase": "RESEARCH",
                "result_status": "SUCCESS",
                "summary": "Batch SIM_A complete, advanced to SIM_B",
            }
        if len(calls) == 2:
            return {
                "status": WorkflowStatus.AUTO_CONTINUE.value,
                "batch": "BATCH_SIM_B",
                "phase": "RESEARCH",
                "result_status": "SUCCESS",
                "summary": "SIM_B research started",
            }
        return {
            "status": WorkflowStatus.RETRY.value,
            "batch": "BATCH_SIM_B",
            "phase": "RESEARCH",
            "result_status": "PARTIAL",
            "summary": "still working",
        }

    monkeypatch.setattr(runner.runner, "run_autonomous_step", fake_step)
    monkeypatch.setattr(runner, "all_confirmed_services_complete", lambda: False)

    summary = runner.run_until_terminal(max_ticks=2, steps_per_tick=5)

    assert summary["status"] == "IN_PROGRESS"
    assert len(calls) >= 2
    assert any("BATCH_SIM_B" in c for c in calls)
    batches_seen = {c.split(":")[0] for c in calls}
    assert "BATCH_SIM_A" in batches_seen or "BATCH_SIM_B" in batches_seen


def test_all_confirmed_services_complete(restore_state) -> None:
    runner = OvernightRunner(REPO)
    progress = runner.compute_catalogue_progress()
    assert "services_remaining" in progress
    assert progress["total_confirmed_services"] == 454


def test_heartbeat_fields_present(restore_state) -> None:
    runner = OvernightRunner(REPO)
    state = StateMachine(REPO).load()
    status = runner._build_status(state, started_at=runner._now())
    for field in (
        "started_at",
        "last_activity_at",
        "current_batch",
        "current_phase",
        "services_complete",
        "services_remaining",
        "batches_complete",
        "deployment_locked",
        "mode",
        "agent_id",
    ):
        assert field in status
