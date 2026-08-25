"""Deployment lock tests."""

from __future__ import annotations

import json
from pathlib import Path

from automation.orchestrator.gate_engine import GateEngine
from automation.orchestrator.state_machine import StateMachine


def test_deployment_lock_file_false(tmp_path: Path) -> None:
    lock = tmp_path / "deployment.lock"
    lock.write_text("false\n")
    engine = GateEngine(tmp_path)
    # GateEngine uses repo_root/.automation/deployment.lock — patch path
    engine.automation_dir = tmp_path
    assert engine.read_deployment_lock() is False


def test_project_state_reads_lock_not_json_alone(tmp_path: Path) -> None:
    auto = tmp_path / ".automation"
    auto.mkdir()
    (auto / "deployment.lock").write_text("false\n")
    state_path = auto / "project_state.json"
    state_path.write_text(
        json.dumps(
            {
                "deployment_allowed": True,
                "workflow_status": "READY",
                "project_name": "test",
            }
        )
        + "\n"
    )
    sm = StateMachine(tmp_path)
    state = sm.load()
    assert state.deployment_allowed is False
