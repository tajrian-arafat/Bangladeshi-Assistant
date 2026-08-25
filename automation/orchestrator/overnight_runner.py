"""Overnight autonomous knowledge-construction loop."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.cloud_executor import CloudExecutor
from automation.orchestrator.escalation_manager import EscalationManager
from automation.orchestrator.gate_engine import GateEngine
from automation.orchestrator.logging import write_report
from automation.orchestrator.phase_runner import PhaseRunner
from automation.orchestrator.policy_engine import EscalationPolicy, PolicyEngine
from automation.orchestrator.state_machine import StateMachine
from automation.schemas.state import WorkflowStatus


class OvernightRunner:
    """Run the full RESEARCH→REGRESSION pipeline unattended until catalogue complete or global block."""

    TERMINAL_STATUSES = frozenset(
        {
            "KNOWLEDGE_COMPLETE",
            "KNOWLEDGE_COMPLETE_WITH_DEFERRED_ITEMS",
            "BLOCKED_GLOBAL",
            "EXECUTOR_UNAVAILABLE",
            "STOPPED",
            "PAUSED",
        }
    )

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.state_machine = StateMachine(repo_root)
        self.batch_manager = BatchManager(repo_root)
        self.gates = GateEngine(repo_root)
        self.runner = PhaseRunner(repo_root)
        self.cloud = CloudExecutor(repo_root)
        self.policy = PolicyEngine()
        self.escalation = EscalationManager(repo_root)
        self.status_path = repo_root / ".automation" / "overnight_status.json"
        self.final_state_path = repo_root / ".automation" / "final_project_state.json"
        self.log_path = repo_root / ".automation" / "reports" / "overnight_run.log"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _append_log(self, message: str) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{self._now()}] {message}\n")

    def _load_status(self) -> dict[str, Any]:
        if self.status_path.exists():
            return json.loads(self.status_path.read_text(encoding="utf-8"))
        return {}

    def _save_status(self, payload: dict[str, Any]) -> None:
        self.status_path.parent.mkdir(parents=True, exist_ok=True)
        self.status_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def compute_catalogue_progress(self) -> dict[str, Any]:
        queue = self.batch_manager.load_queue()
        batches = queue.get("batches", [])
        total_confirmed = int(queue.get("confirmed_services_in_catalogue") or 454)

        completed_batches = [b for b in batches if b.get("status") == "COMPLETE"]
        in_progress = [b for b in batches if b.get("status") == "IN_PROGRESS"]
        deferred_batches = [b for b in batches if b.get("status") == "DEFERRED"]
        blocked_batches = [b for b in batches if b.get("status") == "BLOCKED"]

        services_complete = sum(int(b.get("service_count") or 0) for b in completed_batches)
        services_deferred = sum(int(b.get("service_count") or 0) for b in deferred_batches)
        services_blocked = sum(int(b.get("service_count") or 0) for b in blocked_batches)
        services_remaining = max(0, total_confirmed - services_complete - services_deferred)

        return {
            "total_confirmed_services": total_confirmed,
            "researched_services": services_complete + sum(int(b.get("service_count") or 0) for b in in_progress),
            "verified_services": services_complete,
            "published_services": services_complete,
            "partially_covered_services": sum(int(b.get("service_count") or 0) for b in in_progress),
            "deferred_services": services_deferred,
            "blocked_services": services_blocked,
            "completed_services": services_complete,
            "services_remaining": services_remaining,
            "completed_batches": len(completed_batches),
            "total_batches": len(batches),
        }

    def all_confirmed_services_complete(self) -> bool:
        progress = self.compute_catalogue_progress()
        if progress["services_remaining"] > 0:
            return False
        queue = self.batch_manager.load_queue()
        for batch in queue.get("batches", []):
            if batch.get("status") in {"PLANNED", "IN_PROGRESS", "READY"}:
                return False
        return True

    def validate_preflight(self) -> tuple[bool, str]:
        lock = self.gates.assert_deployment_locked()
        if not lock.passed:
            return False, lock.message
        state = self.state_machine.load()
        if state.deployment_allowed:
            return False, "deployment_allowed must remain false"
        return True, "preflight ok"

    def _recover_supervisor_review(self, state) -> None:
        if state.workflow_status != WorkflowStatus.SUPERVISOR_REVIEW.value:
            return
        phase = state.current_phase or ""
        if phase in {"E2E", "REGRESSION"}:
            state.retry_count = 0
            self.state_machine.transition(state, WorkflowStatus.READY)

    def _handle_policy_block(self, decision, state) -> dict[str, Any] | None:
        if decision.policy == EscalationPolicy.BLOCKED_GLOBAL:
            payload = self._build_status(state, global_blocked=True, reason=decision.reason)
            self._save_status(payload)
            return {"status": "BLOCKED_GLOBAL", "reason": decision.reason, "overnight_status": payload}

        if decision.record_deferred_review:
            self.escalation.defer_for_human_review(
                batch=state.current_batch or "UNKNOWN",
                issue=decision.reason,
                severity="MEDIUM",
                recommended_action="Deferred human review — overnight run continued",
            )
        return None

    def _build_status(
        self,
        state,
        *,
        started_at: str | None = None,
        global_blocked: bool = False,
        reason: str = "",
        cloud_handle: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        progress = self.compute_catalogue_progress()
        existing = self._load_status()
        cloud_fields = self.cloud.overnight_status_fields(None, last_error=reason if global_blocked else None)
        if cloud_handle:
            cloud_fields.update(cloud_handle)
        deferred_items = len(list((self.repo_root / ".automation" / "decisions").glob("*.json")))
        return {
            "started_at": started_at or existing.get("started_at") or self._now(),
            "last_activity_at": self._now(),
            "current_batch": state.current_batch,
            "current_phase": state.current_phase,
            "current_run_id": state.current_run_id,
            "current_task": f"{state.current_batch}:{state.current_phase}" if state.current_batch else None,
            "workflow_status": state.workflow_status,
            "services_complete": progress["completed_services"],
            "services_remaining": progress["services_remaining"],
            "batches_complete": progress["completed_batches"],
            "deferred_items": deferred_items,
            "deferred_count": progress["deferred_services"],
            "global_blocked": global_blocked,
            "global_block_reason": reason,
            "deployment_locked": not self.gates.read_deployment_lock(),
            "catalogue_progress": progress,
            **cloud_fields,
        }

    def _ensure_active_batch(self, state) -> bool:
        """Ensure state points at the next pending batch; return False if catalogue is done."""
        self.batch_manager.sync_completed_batches(state.idempotency_keys)
        state = self.state_machine.load()

        if state.current_batch:
            batch = self.batch_manager.get_batch(state.current_batch)
            regression_done = f"{state.current_batch}:REGRESSION:complete" in (state.idempotency_keys or [])
            if batch and batch.get("status") == "COMPLETE":
                return self._advance_to_next_batch(state)
            if regression_done and state.continuous_mode:
                self.batch_manager.mark_batch_status(state.current_batch, "COMPLETE")
                state.last_completed_batch = state.current_batch
                self.state_machine.save(state)
                return self._advance_to_next_batch(state)
            if batch and batch.get("status") != "COMPLETE":
                if batch.get("status") == "PLANNED":
                    self.batch_manager.mark_batch_status(state.current_batch, "IN_PROGRESS")
                if state.current_phase == "STABILIZATION" and state.continuous_mode:
                    state.current_phase = "REGRESSION"
                    self.state_machine.save(state)
                return True

        if self._advance_to_next_batch(state):
            return True

        return not self.all_confirmed_services_complete()

    def _advance_to_next_batch(self, state) -> bool:
        if self.all_confirmed_services_complete():
            return False
        next_batch = self.batch_manager.next_pending_batch(state.last_completed_batch)
        if not next_batch:
            return False
        state.current_batch = next_batch["batch_id"]
        state.current_phase = "RESEARCH"
        state.current_run_id = None
        state.retry_count = 0
        state.pending_escalations = []
        self.batch_manager.mark_batch_status(next_batch["batch_id"], "IN_PROGRESS")
        if state.workflow_status != WorkflowStatus.READY.value:
            self.state_machine.transition(state, WorkflowStatus.READY)
        else:
            self.state_machine.save(state)
        self._append_log(f"Advanced to {next_batch['batch_id']} RESEARCH")
        return True

    def _resolve_step_outcome(self, state, report: dict[str, Any]) -> dict[str, Any] | None:
        """Apply policy to a step outcome. Returns terminal payload only for global blocks."""
        status = report.get("status")
        phase = state.current_phase or report.get("phase") or ""

        if status == WorkflowStatus.SUPERVISOR_REVIEW.value:
            decision = self.policy.evaluate_phase_outcome(
                phase=phase,
                result={
                    "summary": report.get("summary") or "",
                    "status": report.get("result_status") or "",
                    "regressions": 1,
                },
                workflow_status=status,
                retry_count=state.retry_count,
            )
            terminal = self._handle_policy_block(decision, state)
            if terminal:
                return terminal
            if decision.continue_workflow:
                self._recover_supervisor_review(state)
            return None

        if status == WorkflowStatus.HUMAN_APPROVAL_REQUIRED.value:
            decision = self.policy.evaluate_phase_outcome(
                phase=phase,
                result={"summary": report.get("summary") or "", "requires_escalation": True},
                workflow_status=status,
                retry_count=state.retry_count,
            )
            terminal = self._handle_policy_block(decision, state)
            if terminal:
                return terminal
            if decision.continue_workflow:
                state = self.state_machine.load()
                state.pending_escalations = []
                if state.current_phase == "PUBLICATION":
                    state.current_phase = "E2E"
                self.state_machine.transition(state, WorkflowStatus.RUNNING)
            return None

        if status == WorkflowStatus.BLOCKED.value:
            decision = self.policy.evaluate_phase_outcome(
                phase=phase,
                result={
                    "summary": report.get("summary") or "",
                    "status": "BLOCKED",
                    "hallucinations": 0,
                    "regressions": 1,
                },
                workflow_status=status,
                retry_count=state.retry_count,
            )
            terminal = self._handle_policy_block(decision, state)
            if terminal:
                return terminal
            if decision.continue_workflow:
                state = self.state_machine.load()
                state.retry_count = 0
                self.state_machine.transition(state, WorkflowStatus.READY)
            return None

        if report.get("result_status") == "PARTIAL":
            summary = (report.get("summary") or "").lower()
            if "executor_unavailable" in summary or "executor unavailable" in summary:
                if state.retry_count >= 3:
                    payload = self._build_status(state, global_blocked=True, reason=report.get("summary", ""))
                    self._save_status(payload)
                    return {"status": "EXECUTOR_UNAVAILABLE", "reason": report.get("summary"), "overnight_status": payload}
                state.retry_count += 1
                self.state_machine.save(state)
            return None

        return None

    def _should_continue_after_step(self, state, report: dict[str, Any]) -> bool:
        state = self.state_machine.load()
        if state.workflow_status in {WorkflowStatus.PAUSED.value, WorkflowStatus.STOPPED.value}:
            return False

        if state.workflow_status == WorkflowStatus.COMPLETE.value and not state.current_batch:
            return self._advance_to_next_batch(state)

        if report.get("result_status") == "PARTIAL":
            return True

        return state.workflow_status in {
            WorkflowStatus.AUTO_CONTINUE.value,
            WorkflowStatus.RUNNING.value,
            WorkflowStatus.READY.value,
            WorkflowStatus.RETRY.value,
            WorkflowStatus.GAP_CLOSURE.value,
            WorkflowStatus.WAITING_FOR_RESULT.value,
            WorkflowStatus.VALIDATING_RESULT.value,
        }

    def run_final_global_audit(self) -> dict[str, Any]:
        progress = self.compute_catalogue_progress()
        state = self.state_machine.load()
        audit_path = self.repo_root / "docs" / "evaluation" / "FINAL_KNOWLEDGE_CONSTRUCTION_AUDIT.md"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text(
            f"# Final Knowledge Construction Audit\n\n"
            f"Generated: {self._now()}\n\n"
            f"## Catalogue Coverage\n\n"
            f"- Total confirmed services: {progress['total_confirmed_services']}\n"
            f"- Completed services: {progress['completed_services']}\n"
            f"- Remaining services: {progress['services_remaining']}\n"
            f"- Deferred services: {progress['deferred_services']}\n"
            f"- Completed batches: {progress['completed_batches']} / {progress['total_batches']}\n\n"
            f"## Safety\n\n"
            f"- Deployment locked: {not self.gates.read_deployment_lock() is False}\n"
            f"- deployment_allowed: false\n"
            f"- Mode: LOCAL_DEV_ONLY\n\n"
            f"## Last Completed Batch\n\n"
            f"{state.last_completed_batch or 'none'}\n",
            encoding="utf-8",
        )
        return {"audit_path": str(audit_path), "progress": progress}

    def _finalize_terminal(
        self,
        *,
        started_at: str,
        status_label: str,
        ticks: list[dict[str, Any]],
        total_steps: int,
        global_blocked: bool = False,
        block_reason: str = "",
    ) -> dict[str, Any]:
        state = self.state_machine.load()
        progress = self.compute_catalogue_progress()
        overnight_status = self._build_status(
            state,
            started_at=started_at,
            global_blocked=global_blocked,
            reason=block_reason,
        )
        self._save_status(overnight_status)

        final_payload = {
            "status": status_label,
            "updated_at": self._now(),
            "deployment_allowed": False,
            "catalogue_progress": progress,
            "last_completed_batch": state.last_completed_batch,
            "current_batch": state.current_batch,
            "workflow_status": state.workflow_status,
            "overnight_ticks": len(ticks),
            "total_autonomous_steps": total_steps,
        }
        self.final_state_path.write_text(json.dumps(final_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_report(self.repo_root, "overnight_summary.json", {"ticks": ticks, "final": final_payload})
        self._append_log(f"Terminal: {status_label}")
        return {
            "status": status_label,
            "ticks": len(ticks),
            "total_steps": total_steps,
            "global_blocked": global_blocked,
            "catalogue_progress": progress,
            "overnight_status": overnight_status,
        }

    def run_until_terminal(
        self,
        *,
        max_ticks: int | None = None,
        steps_per_tick: int = 25,
    ) -> dict[str, Any]:
        """Long-running autonomous loop — continues across batches until terminal condition."""
        ok, msg = self.validate_preflight()
        if not ok:
            payload = {
                "started_at": self._now(),
                "last_activity_at": self._now(),
                "global_blocked": True,
                "global_block_reason": msg,
                "deployment_locked": not self.gates.read_deployment_lock(),
            }
            self._save_status(payload)
            return {"status": "BLOCKED_GLOBAL", "reason": msg}

        state = self.state_machine.load()
        state.continuous_mode = True
        state.pilot_mode = False
        self.state_machine.save(state)
        self._ensure_active_batch(state)

        started_at = self._now()
        self._append_log("Overnight run_until_terminal started")
        ticks: list[dict[str, Any]] = []
        total_steps = 0
        tick = 0

        while max_ticks is None or tick < max_ticks:
            state = self.state_machine.load()

            if state.workflow_status in {WorkflowStatus.PAUSED.value, WorkflowStatus.STOPPED.value}:
                label = "PAUSED" if state.workflow_status == WorkflowStatus.PAUSED.value else "STOPPED"
                return self._finalize_terminal(
                    started_at=started_at,
                    status_label=label,
                    ticks=ticks,
                    total_steps=total_steps,
                )

            if self.all_confirmed_services_complete():
                self.run_final_global_audit()
                progress = self.compute_catalogue_progress()
                label = (
                    "KNOWLEDGE_COMPLETE"
                    if progress["deferred_services"] == 0
                    else "KNOWLEDGE_COMPLETE_WITH_DEFERRED_ITEMS"
                )
                return self._finalize_terminal(
                    started_at=started_at,
                    status_label=label,
                    ticks=ticks,
                    total_steps=total_steps,
                )

            if not self._ensure_active_batch(state):
                if self.all_confirmed_services_complete():
                    self.run_final_global_audit()
                    return self._finalize_terminal(
                        started_at=started_at,
                        status_label="KNOWLEDGE_COMPLETE",
                        ticks=ticks,
                        total_steps=total_steps,
                    )
                break

            state = self.state_machine.load()
            self._recover_supervisor_review(state)
            batch_before = state.current_batch
            phase_before = state.current_phase

            tick_steps: list[dict[str, Any]] = []
            for _ in range(steps_per_tick):
                state = self.state_machine.load()
                if state.workflow_status in {WorkflowStatus.PAUSED.value, WorkflowStatus.STOPPED.value}:
                    break

                report = self.runner.run_autonomous_step(state)
                tick_steps.append(report)
                total_steps += 1

                terminal = self._resolve_step_outcome(self.state_machine.load(), report)
                if terminal:
                    return terminal

                state = self.state_machine.load()
                self._save_status(self._build_status(state, started_at=started_at))
                self._append_log(
                    f"step {state.current_batch}:{state.current_phase} "
                    f"status={report.get('status')} result={report.get('result_status')}"
                )

                if not self._should_continue_after_step(state, report):
                    break

                state = self.state_machine.load()
                if state.workflow_status == WorkflowStatus.COMPLETE.value and not state.current_batch:
                    if self._advance_to_next_batch(state):
                        break

            state = self.state_machine.load()
            tick_summary = {
                "tick": tick,
                "batch_before": batch_before,
                "batch_after": state.current_batch,
                "phase_before": phase_before,
                "phase_after": state.current_phase,
                "steps": len(tick_steps),
                "last": tick_steps[-1] if tick_steps else None,
                "workflow_status": state.workflow_status,
            }
            ticks.append(tick_summary)
            write_report(self.repo_root, "overnight_summary.json", {"ticks": ticks, "last_tick": tick_summary})

            if batch_before and state.current_batch and batch_before != state.current_batch:
                self._append_log(f"Batch transition {batch_before} -> {state.current_batch}")

            if self.all_confirmed_services_complete():
                self.run_final_global_audit()
                progress = self.compute_catalogue_progress()
                label = (
                    "KNOWLEDGE_COMPLETE"
                    if progress["deferred_services"] == 0
                    else "KNOWLEDGE_COMPLETE_WITH_DEFERRED_ITEMS"
                )
                return self._finalize_terminal(
                    started_at=started_at,
                    status_label=label,
                    ticks=ticks,
                    total_steps=total_steps,
                )

            tick += 1

        state = self.state_machine.load()
        progress = self.compute_catalogue_progress()
        label = "IN_PROGRESS" if progress["services_remaining"] > 0 else "KNOWLEDGE_COMPLETE"
        return self._finalize_terminal(
            started_at=started_at,
            status_label=label,
            ticks=ticks,
            total_steps=total_steps,
        )

    def run(
        self,
        *,
        max_ticks: int | None = None,
        steps_per_tick: int = 25,
    ) -> dict[str, Any]:
        """Backward-compatible entry — delegates to run_until_terminal."""
        return self.run_until_terminal(max_ticks=max_ticks, steps_per_tick=steps_per_tick)
