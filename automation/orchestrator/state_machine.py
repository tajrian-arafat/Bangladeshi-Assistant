"""Workflow state machine persistence and transitions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from automation.schemas.state import ProjectState, WorkflowStatus, assert_transition


class StateMachine:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.state_path = repo_root / ".automation" / "project_state.json"
        self.current_run_path = repo_root / ".automation" / "current_run.json"

    def load(self) -> ProjectState:
        if not self.state_path.exists():
            raise FileNotFoundError(f"Missing project state: {self.state_path}")
        data = json.loads(self.state_path.read_text(encoding="utf-8"))
        # deployment_allowed always from lock file, never trust JSON alone
        from automation.orchestrator.gate_engine import GateEngine

        data["deployment_allowed"] = GateEngine(self.repo_root).read_deployment_lock()
        return ProjectState.from_dict(data)

    def save(self, state: ProjectState) -> None:
        from automation.orchestrator.gate_engine import GateEngine

        state.deployment_allowed = GateEngine(self.repo_root).read_deployment_lock()
        state.updated_at = datetime.now(timezone.utc).isoformat()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def transition(self, state: ProjectState, nxt: WorkflowStatus) -> ProjectState:
        current = WorkflowStatus(state.workflow_status)
        assert_transition(current, nxt)
        state.workflow_status = nxt.value
        self.save(state)
        return state

    def write_current_run(self, payload: dict) -> None:
        self.current_run_path.parent.mkdir(parents=True, exist_ok=True)
        self.current_run_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def read_current_run(self) -> dict | None:
        if not self.current_run_path.exists():
            return None
        return json.loads(self.current_run_path.read_text(encoding="utf-8"))

    def clear_current_run(self) -> None:
        if self.current_run_path.exists():
            self.current_run_path.unlink()
