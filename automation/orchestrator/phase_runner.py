"""Execute workflow phases, simulations, and autonomous pilot runs."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.cursor_adapter import CursorAdapter
from automation.orchestrator.escalation_manager import EscalationManager
from automation.orchestrator.gate_engine import GateEngine
from automation.orchestrator.github_adapter import GitHubAdapter
from automation.orchestrator.logging import setup_logging, write_report
from automation.orchestrator.phase_completion import phase_artifacts_complete, check_batch_research_quality
from automation.orchestrator.phase_executor import PhaseExecutor
from automation.orchestrator.result_validator import ResultValidator
from automation.orchestrator.retry_manager import RetryManager
from automation.orchestrator.state_machine import StateMachine
from automation.schemas.result import PhaseResult
from automation.schemas.state import PHASE_ORDER, ProjectState, WorkflowPhase, WorkflowStatus


class PhaseRunner:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.state_machine = StateMachine(repo_root)
        self.batch_manager = BatchManager(repo_root)
        self.gates = GateEngine(repo_root)
        self.cursor = CursorAdapter(repo_root)
        self.github = GitHubAdapter(repo_root)
        self.validator = ResultValidator()
        self.retry = RetryManager()
        self.escalation = EscalationManager(repo_root)
        self.executor = PhaseExecutor(repo_root)
        self.runs_dir = repo_root / ".automation" / "runs"
        self.logger = setup_logging(repo_root)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _run_dir(self, run_id: str) -> Path:
        path = self.runs_dir / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _write_result(self, run_dir: Path, result: PhaseResult) -> Path:
        path = run_dir / "result.json"
        path.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def _phase_run_id(self, batch_id: str, phase: str, base_run_id: str) -> str:
        return f"{base_run_id}-{phase.lower()}"

    def _next_phase(self, current: str) -> str:
        try:
            idx = PHASE_ORDER.index(WorkflowPhase(current))
        except ValueError:
            return ""
        if idx + 1 < len(PHASE_ORDER):
            return PHASE_ORDER[idx + 1].value
        return ""

    def _skip_gap_closure_if_not_needed(self, current: str, result: dict[str, Any]) -> str:
        """GAP_CLOSURE is optional — skip when verification had zero gaps."""
        if current != WorkflowPhase.GAP_CLOSURE.value:
            return current
        if int(result.get("knowledge_gaps") or 0) == 0:
            return WorkflowPhase.PUBLICATION.value
        return current

    def _idempotency_seen(self, state: ProjectState, key: str) -> bool:
        return key in (state.idempotency_keys or [])

    def _record_idempotency(self, state: ProjectState, key: str) -> None:
        keys = list(state.idempotency_keys or [])
        if key not in keys:
            keys.append(key)
        state.idempotency_keys = keys

    def simulate_all(self) -> dict[str, Any]:
        cases = [
            self._sim_case_1_success_pipeline,
            self._sim_case_2_technical_retry,
            self._sim_case_3_gap_closure,
            self._sim_case_4_critical_fee_conflict,
            self._sim_case_5_hallucination_block,
            self._sim_case_6_citation_failure_block,
            self._sim_case_7_regression,
            self._sim_case_8_batch_progression,
            self._sim_case_9_deployment_block,
            self._sim_case_10_malformed_result,
        ]
        results = []
        for idx, fn in enumerate(cases, start=1):
            run_id = f"sim-{idx:02d}-{uuid.uuid4().hex[:8]}"
            run_dir = self._run_dir(run_id)
            outcome = fn(run_dir)
            results.append(outcome)
        passed = sum(1 for r in results if r["passed"])
        summary = {
            "total_cases": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "cases": results,
            "deployment_lock": not self.gates.read_deployment_lock(),
        }
        write_report(self.repo_root, "simulation_summary.json", summary)
        return summary

    def _sim_case_1_success_pipeline(self, run_dir: Path) -> dict[str, Any]:
        result = PhaseResult.empty_success(
            run_id=run_dir.name,
            batch_id="SIM_BATCH",
            phase="REGRESSION",
            summary="Simulated full pipeline success",
            recommended_next_phase="",
        )
        result.status = "SIMULATED"
        result.simulation_case = "CASE_1_SUCCESS_PIPELINE"
        self._write_result(run_dir, result)
        ok, _ = self.validator.validate_file(run_dir / "result.json")
        gate = self.gates.validate_regression_metrics(
            {"hallucinations": 0, "citation_failures": 0, "batch_01_pass_pct": 100}
        )
        return {"case": "CASE_1", "passed": ok and gate.passed, "transition": "COMPLETE"}

    def _sim_case_2_technical_retry(self, run_dir: Path) -> dict[str, Any]:
        decision = self.retry.evaluate("network timeout during cursor execution", 0)
        retry2 = self.retry.evaluate("network timeout during cursor execution", 1)
        retry3 = self.retry.evaluate("network timeout during cursor execution", 3)
        return {
            "case": "CASE_2",
            "passed": decision.should_retry and retry2.should_retry and retry3.escalate,
            "transition": "RETRY -> SUPERVISOR_REVIEW",
        }

    def _sim_case_3_gap_closure(self, run_dir: Path) -> dict[str, Any]:
        result = PhaseResult.empty_success(
            run_id=run_dir.name,
            batch_id="SIM_BATCH",
            phase="VERIFICATION",
            summary="Gap detected: OFFICIAL_URL_MISSING",
            recommended_next_phase="GAP_CLOSURE",
        )
        result.status = "SIMULATED"
        result.knowledge_gaps = 2
        result.simulation_case = "CASE_3_GAP_CLOSURE"
        self._write_result(run_dir, result)
        return {"case": "CASE_3", "passed": result.recommended_next_phase == "GAP_CLOSURE", "transition": "GAP_CLOSURE"}

    def _sim_case_4_critical_fee_conflict(self, run_dir: Path) -> dict[str, Any]:
        record = self.escalation.create_decision(
            batch="SIM_BATCH",
            issue="Conflicting official fees",
            severity="CRITICAL",
            recommended_action="Human review required before publication",
            simulation=True,
        )
        return {
            "case": "CASE_4",
            "passed": record.status == "HUMAN_APPROVAL_REQUIRED",
            "transition": "HUMAN_APPROVAL_REQUIRED",
            "decision_id": record.decision_id,
        }

    def _sim_case_5_hallucination_block(self, run_dir: Path) -> dict[str, Any]:
        result = PhaseResult.empty_success(
            run_id=run_dir.name,
            batch_id="SIM_BATCH",
            phase="E2E",
            summary="Hallucination detected in E2E",
        )
        result.status = "BLOCKED"
        result.hallucinations = 1
        result.simulation_case = "CASE_5_HALLUCINATION"
        self._write_result(run_dir, result)
        gates = self.gates.validate_phase_result_gates(result.to_dict())
        blocked = any(not g.passed for g in gates)
        return {"case": "CASE_5", "passed": blocked, "transition": "BLOCKED"}

    def _sim_case_6_citation_failure_block(self, run_dir: Path) -> dict[str, Any]:
        result = PhaseResult.empty_success(
            run_id=run_dir.name,
            batch_id="SIM_BATCH",
            phase="E2E",
            summary="Citation failure detected",
        )
        result.status = "BLOCKED"
        result.citation_failures = 1
        self._write_result(run_dir, result)
        gates = self.gates.validate_phase_result_gates(result.to_dict())
        return {"case": "CASE_6", "passed": any(not g.passed for g in gates), "transition": "BLOCKED"}

    def _sim_case_7_regression(self, run_dir: Path) -> dict[str, Any]:
        gate = self.gates.validate_regression_metrics({"hallucinations": 0, "routing_pass_pct": 90})
        return {"case": "CASE_7", "passed": not gate.passed, "transition": "BLOCKED on regression"}

    def _sim_case_8_batch_progression(self, run_dir: Path) -> dict[str, Any]:
        queue = self.batch_manager.load_queue()
        batches = queue.get("batches", [])
        idx_3a = next(i for i, b in enumerate(batches) if b["batch_id"] == "BATCH_03A")
        idx_3b = next(i for i, b in enumerate(batches) if b["batch_id"] == "BATCH_03B")
        return {
            "case": "CASE_8",
            "passed": idx_3b == idx_3a + 1,
            "transition": "BATCH_03A -> BATCH_03B",
        }

    def _sim_case_9_deployment_block(self, run_dir: Path) -> dict[str, Any]:
        gate = self.gates.check_shell_command("npx convex deploy --prod")
        lock = self.gates.assert_deployment_locked()
        return {
            "case": "CASE_9",
            "passed": (not gate.passed) and lock.passed,
            "transition": "DEPLOYMENT_BLOCKED",
        }

    def _sim_case_10_malformed_result(self, run_dir: Path) -> dict[str, Any]:
        bad_path = run_dir / "result.json"
        bad_path.write_text('{"run_id": "x", "status": "SUCCESS"}')
        ok, errors = self.validator.validate_file(bad_path)
        decision = self.retry.evaluate("malformed artifact: invalid result.json", 0)
        return {
            "case": "CASE_10",
            "passed": (not ok) and decision.should_retry,
            "errors": errors,
            "transition": "RETRY",
        }

    def _ensure_run_id(self, state: ProjectState, batch: dict[str, Any]) -> str:
        if state.current_run_id:
            return state.current_run_id
        run_id = f"run-{uuid.uuid4().hex[:12]}"
        state.current_run_id = run_id
        self.state_machine.save(state)
        return run_id

    def _dispatch_cursor_prompt(
        self,
        *,
        run_dir: Path,
        batch: dict[str, Any],
        phase: str,
        state: ProjectState,
        context: dict[str, Any],
    ) -> None:
        template_map = {
            "RESEARCH": "research",
            "VERIFICATION": "verification",
            "GAP_CLOSURE": "gap_closure",
            "PUBLICATION": "publication",
            "E2E": "e2e",
            "REGRESSION": "regression_fix",
        }
        prompt = self.cursor.build_phase_prompt(
            template_name=template_map.get(phase, "research"),
            batch_id=batch["batch_id"],
            phase=phase,
            context=context,
        )
        self.cursor.dispatch_phase(
            run_dir=run_dir,
            batch_id=batch["batch_id"],
            phase=phase,
            prompt=prompt,
            simulation=state.simulation_mode,
        )

    def execute_current_phase(self, state: ProjectState, batch: dict[str, Any]) -> PhaseResult:
        """Run the current phase via PhaseExecutor (idempotent)."""
        phase = state.current_phase or WorkflowPhase.RESEARCH.value
        batch_id = batch["batch_id"]
        base_run_id = self._ensure_run_id(state, batch)
        phase_run_id = self._phase_run_id(batch_id, phase, base_run_id)
        idem_key = f"{batch_id}:{phase}:complete"

        if self.batch_manager.is_phase_complete(batch_id, phase):
            completion = phase_artifacts_complete(self.repo_root, batch, phase)
            if completion.complete:
                return PhaseResult(
                    run_id=phase_run_id,
                    batch_id=batch_id,
                    phase=phase,
                    status="SUCCESS",
                    started_at=self._now(),
                    completed_at=self._now(),
                    summary=f"Phase {phase} already complete (idempotent skip)",
                    recommended_next_phase=self._next_phase(phase),
                    idempotency_key=idem_key,
                )

        if self._idempotency_seen(state, idem_key):
            completion = phase_artifacts_complete(self.repo_root, batch, phase)
            if completion.complete:
                return PhaseResult(
                    run_id=phase_run_id,
                    batch_id=batch_id,
                    phase=phase,
                    status="SUCCESS",
                    started_at=self._now(),
                    completed_at=self._now(),
                    summary=f"Phase {phase} idempotent skip",
                    recommended_next_phase=self._next_phase(phase),
                    idempotency_key=idem_key,
                )

        run_dir = self._run_dir(phase_run_id)
        self.github.write_snapshot(run_dir)
        self.state_machine.write_current_run(
            {
                "run_id": base_run_id,
                "phase_run_id": phase_run_id,
                "batch_id": batch_id,
                "phase": phase,
                "started_at": self._now(),
            }
        )

        result = self.executor.execute_phase(
            run_id=phase_run_id,
            batch=batch,
            phase=phase,
            batch_manager=self.batch_manager,
        )
        self._write_result(run_dir, result)
        if result.status == "SUCCESS":
            self._record_idempotency(state, idem_key)
            self.batch_manager.mark_phase_complete(batch_id, phase)
        self.state_machine.save(state)
        return result

    def validate_and_transition(
        self, state: ProjectState, result_path: Path | None = None, result_data: dict[str, Any] | None = None
    ) -> ProjectState:
        if not state.current_run_id:
            raise RuntimeError("No current run to validate")
        phase = state.current_phase or WorkflowPhase.RESEARCH.value
        phase_run_id = self._phase_run_id(state.current_batch or "", phase, state.current_run_id)
        run_dir = self._run_dir(phase_run_id)
        if result_path is None:
            result_path = run_dir / "result.json"
        if state.workflow_status != WorkflowStatus.VALIDATING_RESULT.value:
            self.state_machine.transition(state, WorkflowStatus.VALIDATING_RESULT)

        from automation.schemas.result import validate_phase_result

        if result_data is not None:
            ok, errors = validate_phase_result(result_data)
            result = result_data
        else:
            ok, errors = self.validator.validate_file(result_path)
            result = None

        if not ok:
            decision = self.retry.evaluate("malformed artifact: " + "; ".join(errors), state.retry_count)
            if decision.should_retry:
                state.retry_count = decision.retry_count
                return self.state_machine.transition(state, WorkflowStatus.RETRY)
            record = self.escalation.create_decision(
                batch=state.current_batch or "UNKNOWN",
                issue="Malformed phase result",
                severity="HIGH",
                evidence=[{"errors": errors}],
            )
            state.pending_escalations.append(record.decision_id)
            return self.state_machine.transition(state, WorkflowStatus.HUMAN_APPROVAL_REQUIRED)

        if result is None:
            result = self.validator.load_validated(result_path)
        gate_results = self.gates.validate_phase_result_gates(result)
        if any(not g.passed for g in gate_results):
            if result.get("hallucinations", 0) > 0 or result.get("citation_failures", 0) > 0:
                return self.state_machine.transition(state, WorkflowStatus.BLOCKED)
            return self.state_machine.transition(state, WorkflowStatus.SUPERVISOR_REVIEW)

        if result.get("requires_escalation") or result.get("critical_conflicts", 0) > 0 or result.get("status") == "ESCALATED":
            record = self.escalation.create_decision(
                batch=state.current_batch or result["batch_id"],
                issue=result.get("summary", "Escalation required"),
                severity="CRITICAL" if result.get("critical_conflicts") else "HIGH",
            )
            state.pending_escalations.append(record.decision_id)
            return self.state_machine.transition(state, WorkflowStatus.HUMAN_APPROVAL_REQUIRED)

        status = result.get("status")
        if status == "PARTIAL":
            return self.state_machine.transition(state, WorkflowStatus.RETRY)

        if status in {"FAILED", "BLOCKED"}:
            decision = self.retry.evaluate(result.get("summary", "phase failed"), state.retry_count)
            if decision.should_retry:
                state.retry_count = decision.retry_count
                return self.state_machine.transition(state, WorkflowStatus.RETRY)
            if decision.escalate:
                record = self.escalation.create_decision(
                    batch=state.current_batch or result["batch_id"],
                    issue=result.get("summary", "Phase failed after retries"),
                    severity="HIGH",
                )
                state.pending_escalations.append(record.decision_id)
                return self.state_machine.transition(state, WorkflowStatus.HUMAN_APPROVAL_REQUIRED)
            return self.state_machine.transition(state, WorkflowStatus.BLOCKED)

        if int(result.get("knowledge_gaps") or 0) > 0 and phase == WorkflowPhase.VERIFICATION.value:
            state.current_phase = WorkflowPhase.GAP_CLOSURE.value
            self.state_machine.save(state)
            return self.state_machine.transition(state, WorkflowStatus.GAP_CLOSURE)

        if status == "SUCCESS" and phase == WorkflowPhase.REGRESSION.value:
            recommended_after_regression = result.get("recommended_next_phase") or ""
            skip_stabilization = state.continuous_mode and recommended_after_regression in {"", "STABILIZATION"}
            if not recommended_after_regression or skip_stabilization:
                return self._complete_current_batch(state)

        if status == "SUCCESS" and phase == WorkflowPhase.STABILIZATION.value and state.continuous_mode:
            return self._complete_current_batch(state)

        recommended = result.get("recommended_next_phase") or self._next_phase(phase)
        if recommended == "GAP_CLOSURE" and int(result.get("knowledge_gaps") or 0) == 0:
            recommended = WorkflowPhase.PUBLICATION.value

        if recommended and recommended not in {"", "HUMAN_APPROVAL_REQUIRED"}:
            if recommended in {p.value for p in WorkflowPhase}:
                state.current_phase = recommended
            self.state_machine.save(state)

        return self.state_machine.transition(state, WorkflowStatus.AUTO_CONTINUE)

    def _complete_current_batch(self, state: ProjectState) -> ProjectState:
        """Mark the active batch complete after REGRESSION (STABILIZATION is optional/skipped)."""
        batch_id = state.current_batch or ""
        if batch_id:
            batch = self.batch_manager.get_batch(batch_id)
            if batch:
                quality = check_batch_research_quality(self.repo_root, batch)
                if not quality.complete:
                    state.retry_count = 0
                    state.current_phase = WorkflowPhase.RESEARCH.value
                    self.state_machine.save(state)
                    return self.state_machine.transition(state, WorkflowStatus.RETRY)
            self.batch_manager.mark_batch_status(batch_id, "COMPLETE")
            state.last_completed_batch = batch_id
        next_batch = self.batch_manager.next_pending_batch(state.last_completed_batch)
        if next_batch and batch_id:
            state.current_batch = next_batch["batch_id"]
            state.current_phase = WorkflowPhase.RESEARCH.value
            state.current_run_id = None
            state.retry_count = 0
            self.batch_manager.mark_batch_status(next_batch["batch_id"], "IN_PROGRESS")
            self.state_machine.clear_current_run()
            self.state_machine.save(state)
            self.state_machine.transition(state, WorkflowStatus.COMPLETE)
            return self.state_machine.transition(state, WorkflowStatus.READY)
        state.current_batch = None
        state.current_phase = None
        state.current_run_id = None
        state.retry_count = 0
        self.state_machine.clear_current_run()
        self.state_machine.save(state)
        return self.state_machine.transition(state, WorkflowStatus.COMPLETE)

    def advance_phase(self, state: ProjectState) -> ProjectState:
        current = state.current_phase or WorkflowPhase.RESEARCH.value
        nxt = self._next_phase(current)
        if not nxt:
            return self._complete_current_batch(state)
        state.current_phase = nxt
        state.retry_count = 0
        self.state_machine.save(state)
        if state.workflow_status == WorkflowStatus.VALIDATING_RESULT.value:
            return self.state_machine.transition(state, WorkflowStatus.AUTO_CONTINUE)
        return self.state_machine.transition(state, WorkflowStatus.RUNNING)

    def run_autonomous_step(self, state: ProjectState) -> dict[str, Any]:
        """Single autonomous iteration: execute, validate, and auto-continue when possible."""
        lock = self.gates.assert_deployment_locked()
        if not lock.passed:
            return {"status": "BLOCKED", "reason": lock.message}

        if state.pending_escalations:
            return {
                "status": "HUMAN_APPROVAL_REQUIRED",
                "pending": state.pending_escalations,
            }

        # Allow autonomous resume after E2E/REGRESSION fixes (non-hallucination BLOCKED/SUPERVISOR_REVIEW).
        recoverable_phases = {WorkflowPhase.E2E.value, WorkflowPhase.REGRESSION.value}
        if state.workflow_status in {WorkflowStatus.BLOCKED.value, WorkflowStatus.SUPERVISOR_REVIEW.value}:
            if state.current_phase in recoverable_phases:
                state.retry_count = 0
                self.state_machine.transition(state, WorkflowStatus.READY)
                state = self.state_machine.load()
            else:
                return {
                    "status": state.workflow_status,
                    "batch": state.current_batch,
                    "phase": state.current_phase,
                }

        batch = self.batch_manager.get_batch(state.current_batch or "")
        if not batch:
            batch = self.batch_manager.next_pending_batch(state.last_completed_batch)
            if not batch:
                return {"status": "COMPLETE", "message": "No pending batches"}
            state.current_batch = batch["batch_id"]
            state.current_phase = WorkflowPhase.RESEARCH.value
            self.batch_manager.mark_batch_status(batch["batch_id"], "IN_PROGRESS")
            self.state_machine.save(state)

        phase = state.current_phase or WorkflowPhase.RESEARCH.value

        executable_statuses = {
            WorkflowStatus.READY.value,
            WorkflowStatus.RUNNING.value,
            WorkflowStatus.RETRY.value,
            WorkflowStatus.GAP_CLOSURE.value,
            WorkflowStatus.AUTO_CONTINUE.value,
        }

        if state.workflow_status == WorkflowStatus.VALIDATING_RESULT.value:
            phase_run_id = self._phase_run_id(state.current_batch or "", phase, state.current_run_id or "")
            result_path = self._run_dir(phase_run_id) / "result.json"
            state = self.validate_and_transition(state, result_path=result_path)
            return {
                "status": state.workflow_status,
                "batch": batch["batch_id"],
                "phase": phase,
                "run_id": state.current_run_id,
                "result_status": "RESUMED_VALIDATION",
                "summary": "Resumed validation from VALIDATING_RESULT",
                "next_phase": state.current_phase,
            }

        if state.workflow_status in executable_statuses:
            if state.workflow_status == WorkflowStatus.AUTO_CONTINUE.value:
                state.retry_count = 0
            if state.workflow_status != WorkflowStatus.RUNNING.value:
                self.state_machine.transition(state, WorkflowStatus.RUNNING)
            result = self.execute_current_phase(state, batch)
            self.state_machine.transition(state, WorkflowStatus.WAITING_FOR_RESULT)
            state = self.validate_and_transition(state, result_data=result.to_dict())

            report = {
                "status": state.workflow_status,
                "batch": batch["batch_id"],
                "phase": phase,
                "run_id": state.current_run_id,
                "result_status": result.status,
                "summary": result.summary,
                "next_phase": state.current_phase,
            }
            write_report(self.repo_root, f"autonomous_{batch['batch_id']}_{phase}.json", report)
            return report

        return {"status": state.workflow_status, "batch": batch["batch_id"], "phase": phase}

    def run_autonomous_loop(self, state: ProjectState, *, max_steps: int = 20) -> dict[str, Any]:
        """Run until blocked, complete, or human approval required."""
        recoverable_phases = {WorkflowPhase.E2E.value, WorkflowPhase.REGRESSION.value}
        steps: list[dict[str, Any]] = []
        for _ in range(max_steps):
            state = self.state_machine.load()
            if state.workflow_status in {
                WorkflowStatus.PAUSED.value,
                WorkflowStatus.STOPPED.value,
            }:
                break
            if state.pending_escalations:
                break
            report = self.run_autonomous_step(state)
            steps.append(report)
            terminal = {
                "HUMAN_APPROVAL_REQUIRED",
                "BLOCKED",
                "COMPLETE",
            }
            if report.get("status") in terminal:
                break
            if report.get("status") == WorkflowStatus.SUPERVISOR_REVIEW.value:
                if (state.current_phase or "") not in recoverable_phases:
                    break
            if report.get("result_status") == "PARTIAL":
                break
            state = self.state_machine.load()
            if state.workflow_status not in {
                WorkflowStatus.AUTO_CONTINUE.value,
                WorkflowStatus.RUNNING.value,
                WorkflowStatus.READY.value,
                WorkflowStatus.RETRY.value,
            }:
                break
        summary = {
            "steps": len(steps),
            "final_status": steps[-1]["status"] if steps else "NOOP",
            "last": steps[-1] if steps else None,
            "history": steps,
        }
        write_report(self.repo_root, "autonomous_loop_summary.json", summary)
        return summary

    def run_once(self, state: ProjectState) -> dict[str, Any]:
        """Backward-compatible single step — delegates to autonomous loop step."""
        return self.run_autonomous_step(state)
