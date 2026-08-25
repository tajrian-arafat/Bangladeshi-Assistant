"""Overnight autonomous knowledge-construction loop."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.escalation_manager import EscalationManager
from automation.orchestrator.gate_engine import GateEngine
from automation.orchestrator.logging import write_report
from automation.orchestrator.phase_runner import PhaseRunner
from automation.orchestrator.policy_engine import EscalationPolicy, PolicyEngine
from automation.orchestrator.state_machine import StateMachine
from automation.schemas.state import WorkflowStatus


class OvernightRunner:
    """Run the full RESEARCH→REGRESSION pipeline unattended until catalogue complete or global block."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.state_machine = StateMachine(repo_root)
        self.batch_manager = BatchManager(repo_root)
        self.gates = GateEngine(repo_root)
        self.runner = PhaseRunner(repo_root)
        self.policy = PolicyEngine()
        self.escalation = EscalationManager(repo_root)
        self.status_path = repo_root / ".automation" / "overnight_status.json"
        self.final_state_path = repo_root / ".automation" / "final_project_state.json"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

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
        services_in_progress = sum(int(b.get("service_count") or 0) for b in in_progress)
        services_deferred = sum(int(b.get("service_count") or 0) for b in deferred_batches)
        services_blocked = sum(int(b.get("service_count") or 0) for b in blocked_batches)
        services_remaining = max(0, total_confirmed - services_complete - services_deferred)

        researched = services_complete + services_in_progress
        verified = services_complete
        published = services_complete
        partially_covered = services_in_progress

        return {
            "total_confirmed_services": total_confirmed,
            "researched_services": researched,
            "verified_services": verified,
            "published_services": published,
            "partially_covered_services": partially_covered,
            "deferred_services": services_deferred,
            "blocked_services": services_blocked,
            "completed_services": services_complete,
            "services_remaining": services_remaining,
            "completed_batches": len(completed_batches),
            "total_batches": len(batches),
        }

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

    def _handle_policy_block(self, decision, state) -> dict[str, Any]:
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

        return {}

    def _build_status(
        self,
        state,
        *,
        started_at: str | None = None,
        global_blocked: bool = False,
        reason: str = "",
    ) -> dict[str, Any]:
        progress = self.compute_catalogue_progress()
        existing = self._load_status()
        return {
            "started_at": started_at or existing.get("started_at") or self._now(),
            "last_activity_at": self._now(),
            "current_batch": state.current_batch,
            "current_phase": state.current_phase,
            "current_run_id": state.current_run_id,
            "workflow_status": state.workflow_status,
            "services_complete": progress["completed_services"],
            "services_remaining": progress["services_remaining"],
            "deferred_count": progress["deferred_services"],
            "global_blocked": global_blocked,
            "global_block_reason": reason,
            "deployment_locked": not self.gates.read_deployment_lock(),
            "catalogue_progress": progress,
        }

    def _advance_to_next_batch(self, state) -> bool:
        progress = self.compute_catalogue_progress()
        if progress["services_remaining"] <= 0:
            return False
        next_batch = self.batch_manager.next_pending_batch()
        if not next_batch:
            return False
        state.current_batch = next_batch["batch_id"]
        state.current_phase = "RESEARCH"
        state.current_run_id = None
        state.retry_count = 0
        self.batch_manager.mark_batch_status(next_batch["batch_id"], "IN_PROGRESS")
        self.state_machine.transition(state, WorkflowStatus.READY)
        return True

    def run(
        self,
        *,
        max_steps: int = 500,
        steps_per_tick: int = 25,
    ) -> dict[str, Any]:
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

        started_at = self._now()
        ticks: list[dict[str, Any]] = []
        total_steps = 0
        global_blocked = False
        block_reason = ""

        for tick in range(max_steps):
            state = self.state_machine.load()
            self._recover_supervisor_review(state)
            state = self.state_machine.load()

            if state.workflow_status in {WorkflowStatus.PAUSED.value, WorkflowStatus.STOPPED.value}:
                break

            progress = self.compute_catalogue_progress()
            if (
                state.workflow_status == WorkflowStatus.COMPLETE.value
                and not state.current_batch
                and progress["services_remaining"] > 0
            ):
                if self._advance_to_next_batch(state):
                    state = self.state_machine.load()
                else:
                    break

            if progress["services_remaining"] == 0 and progress["deferred_services"] == 0:
                if state.workflow_status == WorkflowStatus.COMPLETE.value and not state.current_batch:
                    break

            summary = self.runner.run_autonomous_loop(state, max_steps=steps_per_tick)
            total_steps += int(summary.get("steps") or 0)
            ticks.append(summary)
            state = self.state_machine.load()

            last = summary.get("last") or {}
            final_status = summary.get("final_status")

            if final_status == WorkflowStatus.SUPERVISOR_REVIEW.value:
                decision = self.policy.evaluate_phase_outcome(
                    phase=state.current_phase or "",
                    result={
                        "summary": last.get("summary") or "",
                        "status": last.get("result_status") or "",
                        "regressions": 1,
                    },
                    workflow_status=final_status,
                    retry_count=state.retry_count,
                )
                handled = self._handle_policy_block(decision, state)
                if handled:
                    return handled
                if decision.continue_workflow:
                    self._recover_supervisor_review(state)
                    continue

            if final_status == WorkflowStatus.HUMAN_APPROVAL_REQUIRED.value:
                decision = self.policy.evaluate_phase_outcome(
                    phase=state.current_phase or "",
                    result={"summary": last.get("summary") or "", "requires_escalation": True},
                    workflow_status=final_status,
                    retry_count=state.retry_count,
                )
                handled = self._handle_policy_block(decision, state)
                if handled:
                    return handled
                if decision.continue_workflow:
                    state.pending_escalations = []
                    self.state_machine.transition(state, WorkflowStatus.READY)
                    continue
                break

            if final_status == WorkflowStatus.BLOCKED.value:
                decision = self.policy.evaluate_phase_outcome(
                    phase=state.current_phase or "",
                    result={
                        "summary": last.get("summary") or "",
                        "status": "BLOCKED",
                        "hallucinations": 0,
                        "regressions": 1,
                    },
                    workflow_status=final_status,
                    retry_count=state.retry_count,
                )
                handled = self._handle_policy_block(decision, state)
                if handled:
                    return handled
                if decision.continue_workflow:
                    state.retry_count = 0
                    self.state_machine.transition(state, WorkflowStatus.READY)
                    continue
                global_blocked = True
                block_reason = decision.reason
                break

            if final_status == WorkflowStatus.COMPLETE.value and not state.current_batch:
                break

            if final_status in {WorkflowStatus.COMPLETE.value} and state.current_batch:
                next_batch = self.batch_manager.next_ready_batch()
                if next_batch:
                    state.current_batch = next_batch["batch_id"]
                    state.current_phase = "RESEARCH"
                    state.current_run_id = None
                    state.retry_count = 0
                    self.batch_manager.mark_batch_status(next_batch["batch_id"], "IN_PROGRESS")
                    self.state_machine.transition(state, WorkflowStatus.READY)
                    continue

            status_payload = self._build_status(state, started_at=started_at)
            self._save_status(status_payload)

            if final_status not in {
                WorkflowStatus.AUTO_CONTINUE.value,
                WorkflowStatus.RUNNING.value,
                WorkflowStatus.READY.value,
                WorkflowStatus.COMPLETE.value,
            }:
                if final_status != WorkflowStatus.SUPERVISOR_REVIEW.value:
                    break

        state = self.state_machine.load()
        progress = self.compute_catalogue_progress()
        overnight_status = self._build_status(
            state,
            started_at=started_at,
            global_blocked=global_blocked,
            reason=block_reason,
        )
        self._save_status(overnight_status)

        project_complete = progress["services_remaining"] == 0
        final_status_label = (
            "KNOWLEDGE_COMPLETE"
            if project_complete and progress["deferred_services"] == 0
            else "KNOWLEDGE_COMPLETE_WITH_DEFERRED_ITEMS"
            if project_complete
            else "IN_PROGRESS"
            if not global_blocked
            else "BLOCKED_GLOBAL"
        )

        final_payload = {
            "status": final_status_label,
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

        return {
            "status": final_status_label,
            "ticks": len(ticks),
            "total_steps": total_steps,
            "global_blocked": global_blocked,
            "catalogue_progress": progress,
            "overnight_status": overnight_status,
        }
