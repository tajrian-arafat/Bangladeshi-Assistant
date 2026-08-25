"""Cloud execution orchestrator — remote Cursor Cloud Agent or in-process cloud VM."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from automation.orchestrator.cursor_adapter import CursorAdapter, CursorRunHandle
from automation.orchestrator.task_factory import CloudTaskSpec, TaskFactory
from automation.schemas.result import PhaseResult, validate_phase_result
from automation.schemas.state import ProjectState


class ExecutorMode(StrEnum):
    AUTO_CLOUD = "AUTO_CLOUD"
    AUTO_LOCAL = "AUTO_LOCAL"
    MANUAL_RECOVERY = "MANUAL_RECOVERY"


class ExecutionMode(StrEnum):
    REMOTE_CLOUD = "REMOTE_CLOUD"
    IN_PROCESS_CLOUD = "IN_PROCESS_CLOUD"
    LOCAL_DETERMINISTIC = "LOCAL_DETERMINISTIC"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass
class CloudExecutionHandle:
    execution_mode: ExecutionMode
    run_id: str
    agent_id: str | None = None
    agent_run_id: str | None = None
    task_path: Path | None = None
    waiting_for_agent: bool = False
    status: str = "DISPATCHED"


class CloudExecutor:
    MAX_REMOTE_RETRIES = 3
    POLL_INTERVAL_SEC = 10
    MAX_POLL_WAIT_SEC = 3600

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.adapter = CursorAdapter(repo_root)
        self.task_factory = TaskFactory(repo_root)
        self.runs_dir = repo_root / ".automation" / "runs"
        self.mode = ExecutorMode(os.environ.get("BDA_EXECUTOR_MODE", "AUTO_CLOUD"))

    @property
    def in_process_cloud_available(self) -> bool:
        return os.environ.get("CURSOR_AGENT") == "1" and bool(os.environ.get("CURSOR_CONVERSATION_ID"))

    @property
    def current_agent_id(self) -> str | None:
        return os.environ.get("CURSOR_CONVERSATION_ID")

    def executor_available(self) -> bool:
        if self.mode == ExecutorMode.MANUAL_RECOVERY:
            return False
        if self.mode == ExecutorMode.AUTO_LOCAL:
            return True
        return self.adapter.cloud_available or self.in_process_cloud_available

    def build_task(self, batch: dict[str, Any], phase: str, run_id: str, state: ProjectState | None = None) -> CloudTaskSpec:
        builders = {
            "RESEARCH": self.task_factory.create_research_task,
            "VERIFICATION": self.task_factory.create_verification_task,
            "GAP_CLOSURE": self.task_factory.create_gap_closure_task,
            "PUBLICATION": self.task_factory.create_publication_task,
            "E2E": self.task_factory.create_e2e_task,
            "REGRESSION": self.task_factory.create_regression_task,
        }
        fn = builders.get(phase, self.task_factory.build_task)
        if phase in builders:
            return fn(batch, run_id, state)
        return self.task_factory.build_task(batch=batch, phase=phase, run_id=run_id, state=state)

    def dispatch(
        self,
        *,
        batch: dict[str, Any],
        phase: str,
        run_id: str,
        run_dir: Path,
        state: ProjectState | None = None,
    ) -> CloudExecutionHandle:
        task = self.build_task(batch, phase, run_id, state)
        task_path = run_dir / "task.json"
        task.write(task_path)
        (run_dir / "prompt.md").write_text(task.prompt_text, encoding="utf-8")

        if self.mode == ExecutorMode.AUTO_LOCAL:
            return CloudExecutionHandle(
                execution_mode=ExecutionMode.LOCAL_DETERMINISTIC,
                run_id=run_id,
                task_path=task_path,
            )

        if self.adapter.cloud_available:
            last_error = ""
            for attempt in range(1, self.MAX_REMOTE_RETRIES + 1):
                try:
                    created = self.adapter.create_cloud_agent(
                        prompt=task.prompt_text,
                        name=f"bda-{batch['batch_id']}-{phase}-{run_id[:8]}",
                        metadata={
                            "batch_id": batch["batch_id"],
                            "phase": phase,
                            "run_id": run_id,
                            "task_id": task.task_id,
                        },
                    )
                    agent = created.get("agent") or {}
                    run = created.get("run") or {}
                    handle = CloudExecutionHandle(
                        execution_mode=ExecutionMode.REMOTE_CLOUD,
                        run_id=run_id,
                        agent_id=agent.get("id"),
                        agent_run_id=run.get("id"),
                        task_path=task_path,
                        waiting_for_agent=True,
                    )
                    (run_dir / "cursor_handle.json").write_text(
                        json.dumps(
                            {
                                "execution_mode": handle.execution_mode.value,
                                "agent_id": handle.agent_id,
                                "agent_run_id": handle.agent_run_id,
                                "task_id": task.task_id,
                            },
                            indent=2,
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                    return handle
                except Exception as exc:
                    last_error = str(exc)
                    (run_dir / "cloud_error.log").write_text(f"attempt {attempt}: {last_error}\n", encoding="utf-8")
                    time.sleep(min(attempt * 2, 10))

            if self.in_process_cloud_available and self.mode == ExecutorMode.AUTO_CLOUD:
                return CloudExecutionHandle(
                    execution_mode=ExecutionMode.IN_PROCESS_CLOUD,
                    run_id=run_id,
                    agent_id=self.current_agent_id,
                    task_path=task_path,
                )

            raise RuntimeError(f"Remote cloud unavailable after retries: {last_error}")

        if self.in_process_cloud_available:
            return CloudExecutionHandle(
                execution_mode=ExecutionMode.IN_PROCESS_CLOUD,
                run_id=run_id,
                agent_id=self.current_agent_id,
                task_path=task_path,
            )

        return CloudExecutionHandle(
            execution_mode=ExecutionMode.UNAVAILABLE,
            run_id=run_id,
            task_path=task_path,
        )

    def execute_in_process(self, task: CloudTaskSpec, batch: dict[str, Any]) -> PhaseResult:
        from automation.orchestrator.cloud_worker import CloudWorker

        result = CloudWorker(self.repo_root).execute(task, batch)
        result.metadata = {**(result.metadata or {}), "execution_mode": "IN_PROCESS_CLOUD", "agent_id": self.current_agent_id}
        return result

    def wait_for_remote(self, handle: CloudExecutionHandle, run_dir: Path) -> PhaseResult | None:
        if handle.execution_mode != ExecutionMode.REMOTE_CLOUD or not handle.agent_id or not handle.agent_run_id:
            return None

        deadline = time.time() + self.MAX_POLL_WAIT_SEC
        while time.time() < deadline:
            status_payload = self.adapter.get_cloud_run(handle.agent_id, handle.agent_run_id)
            run = status_payload.get("run") or status_payload
            status = (run.get("status") or "").upper()
            if status in {"COMPLETED", "FINISHED", "SUCCEEDED", "SUCCESS"}:
                result_path = run_dir / "result.json"
                if result_path.exists():
                    data = json.loads(result_path.read_text(encoding="utf-8"))
                    ok, _ = validate_phase_result(data)
                    if ok:
                        data["execution_mode"] = "CLOUD"
                        data["agent_id"] = handle.agent_id
                        data["agent_run_id"] = handle.agent_run_id
                        return PhaseResult.from_dict(data)
                return None
            if status in {"FAILED", "CANCELLED", "ERROR"}:
                return None
            time.sleep(self.POLL_INTERVAL_SEC)
        return None

    def enrich_result(self, result: PhaseResult, handle: CloudExecutionHandle) -> PhaseResult:
        meta = dict(result.metadata or {})
        meta["execution_mode"] = handle.execution_mode.value
        if handle.agent_id:
            meta["agent_id"] = handle.agent_id
        if handle.agent_run_id:
            meta["agent_run_id"] = handle.agent_run_id
        result.metadata = meta
        return result

    def write_executor_unavailable_decision(self, batch_id: str, reason: str) -> Path:
        decisions = self.repo_root / ".automation" / "decisions"
        decisions.mkdir(parents=True, exist_ok=True)
        path = decisions / f"executor-unavailable-{batch_id.lower()}.json"
        path.write_text(
            json.dumps(
                {
                    "status": "GLOBAL_BLOCKED",
                    "batch": batch_id,
                    "issue": reason,
                    "severity": "CRITICAL",
                    "recommended_action": "Configure CURSOR_API_KEY or run inside Cursor Cloud Agent VM",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return path

    def overnight_status_fields(self, handle: CloudExecutionHandle | None, *, last_error: str | None = None) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "executor_available": self.executor_available(),
            "agent_id": handle.agent_id if handle else self.current_agent_id,
            "agent_run_id": handle.agent_run_id if handle else None,
            "waiting_for_agent": bool(handle and handle.waiting_for_agent),
            "execution_mode": handle.execution_mode.value if handle else None,
            "last_error": last_error,
            "deployment_locked": True,
        }
