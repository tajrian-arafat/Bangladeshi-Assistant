"""Execute workflow phases, simulations, and pilot runs."""

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

    def _next_phase(self, current: str) -> str:
        try:
            idx = PHASE_ORDER.index(WorkflowPhase(current))
        except ValueError:
            return ""
        if idx + 1 < len(PHASE_ORDER):
            return PHASE_ORDER[idx + 1].value
        return ""

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

    def start_research_phase(self, state: ProjectState, batch: dict[str, Any]) -> PhaseResult:
        run_id = f"run-{uuid.uuid4().hex[:12]}"
        run_dir = self._run_dir(run_id)
        started = self._now()
        artifacts = self.batch_manager.setup_research_artifacts(batch)
        self.github.write_snapshot(run_dir)
        context = {
            "batch": batch,
            "template": "docs/research/BATCH_RESEARCH_TEMPLATE.md",
            "artifacts_created": artifacts,
            "rules": [
                "Never publish during research",
                "Never mark VERIFIED without independent verification",
                "Use authority tiers",
                "Preserve provenance",
            ],
        }
        prompt = self.cursor.build_phase_prompt(
            template_name="research",
            batch_id=batch["batch_id"],
            phase="RESEARCH",
            context=context,
        )
        handle = self.cursor.dispatch_phase(
            run_dir=run_dir,
            batch_id=batch["batch_id"],
            phase="RESEARCH",
            prompt=prompt,
            simulation=state.simulation_mode,
        )
        state.current_run_id = run_id
        state.current_phase = WorkflowPhase.RESEARCH.value
        self.state_machine.save(state)
        self.state_machine.write_current_run(
            {
                "run_id": run_id,
                "batch_id": batch["batch_id"],
                "phase": "RESEARCH",
                "mode": handle.mode,
                "started_at": started,
                "artifacts": artifacts,
            }
        )
        if handle.mode == "local":
            # Pilot: deterministic setup complete; research execution continues via Cursor agent
            result = PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase="RESEARCH",
                status="PARTIAL",
                started_at=started,
                completed_at=self._now(),
                services_total=len(batch.get("service_ids") or []),
                services_processed=0,
                artifacts=artifacts + [str(run_dir / "prompt.md"), str(run_dir / "manifest.json")],
                requires_escalation=False,
                recommended_next_phase="VERIFICATION",
                summary=(
                    f"Research kickoff for {batch['batch_id']}: scope and services_index created. "
                    f"Cursor agent must complete discovery per BATCH_RESEARCH_TEMPLATE.md."
                ),
                idempotency_key=f"{batch['batch_id']}:RESEARCH:setup:{run_id}",
            )
            self._write_result(run_dir, result)
            return result

        result = PhaseResult(
            run_id=run_id,
            batch_id=batch["batch_id"],
            phase="RESEARCH",
            status="PARTIAL",
            started_at=started,
            completed_at=self._now(),
            services_total=len(batch.get("service_ids") or []),
            artifacts=artifacts,
            recommended_next_phase="",
            summary=f"Dispatched to Cursor ({handle.mode}). Awaiting completion.",
            idempotency_key=f"{batch['batch_id']}:RESEARCH:{run_id}",
        )
        self._write_result(run_dir, result)
        return result

    def validate_and_transition(self, state: ProjectState) -> ProjectState:
        if not state.current_run_id:
            raise RuntimeError("No current run to validate")
        run_dir = self._run_dir(state.current_run_id)
        result_path = run_dir / "result.json"
        self.state_machine.transition(state, WorkflowStatus.VALIDATING_RESULT)
        ok, errors = self.validator.validate_file(result_path)
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

        result = self.validator.load_validated(result_path)
        gate_results = self.gates.validate_phase_result_gates(result)
        if any(not g.passed for g in gate_results):
            if result.get("hallucinations", 0) > 0 or result.get("citation_failures", 0) > 0:
                return self.state_machine.transition(state, WorkflowStatus.BLOCKED)
            return self.state_machine.transition(state, WorkflowStatus.SUPERVISOR_REVIEW)

        if result.get("requires_escalation") or result.get("critical_conflicts", 0) > 0:
            record = self.escalation.create_decision(
                batch=state.current_batch or result["batch_id"],
                issue=result.get("summary", "Escalation required"),
                severity="CRITICAL" if result.get("critical_conflicts") else "HIGH",
            )
            state.pending_escalations.append(record.decision_id)
            return self.state_machine.transition(state, WorkflowStatus.HUMAN_APPROVAL_REQUIRED)

        if result.get("knowledge_gaps", 0) > 0 and state.current_phase == WorkflowPhase.VERIFICATION.value:
            return self.state_machine.transition(state, WorkflowStatus.GAP_CLOSURE)

        if result.get("status") == "PARTIAL" and state.pilot_mode:
            # Pilot: allow manual review between phases
            return self.state_machine.transition(state, WorkflowStatus.AUTO_CONTINUE)

        return self.state_machine.transition(state, WorkflowStatus.AUTO_CONTINUE)

    def advance_phase(self, state: ProjectState) -> ProjectState:
        current = state.current_phase or WorkflowPhase.RESEARCH.value
        nxt = self._next_phase(current)
        if not nxt:
            self.batch_manager.mark_batch_status(state.current_batch or "", "COMPLETE")
            state.last_completed_batch = state.current_batch or state.last_completed_batch
            state.current_batch = None
            state.current_phase = None
            state.current_run_id = None
            self.state_machine.clear_current_run()
            return self.state_machine.transition(state, WorkflowStatus.COMPLETE)
        state.current_phase = nxt
        state.retry_count = 0
        return self.state_machine.transition(state, WorkflowStatus.RUNNING)

    def run_once(self, state: ProjectState) -> dict[str, Any]:
        lock = self.gates.assert_deployment_locked()
        if not lock.passed:
            return {"status": "BLOCKED", "reason": lock.message}

        if state.pending_escalations:
            return {
                "status": "HUMAN_APPROVAL_REQUIRED",
                "pending": state.pending_escalations,
            }

        batch = self.batch_manager.get_batch(state.current_batch or "")
        if not batch:
            batch = self.batch_manager.next_ready_batch()
            if not batch:
                return {"status": "COMPLETE", "message": "No ready batches"}
            state.current_batch = batch["batch_id"]
            self.batch_manager.mark_batch_status(batch["batch_id"], "IN_PROGRESS")

        phase = state.current_phase or WorkflowPhase.RESEARCH.value
        self.state_machine.transition(state, WorkflowStatus.RUNNING)

        if phase == WorkflowPhase.RESEARCH.value:
            result = self.start_research_phase(state, batch)
            self.state_machine.transition(state, WorkflowStatus.WAITING_FOR_RESULT)
            if result.status in {"SUCCESS", "PARTIAL", "SIMULATED"}:
                state = self.validate_and_transition(state)
            report = {
                "status": state.workflow_status,
                "batch": batch["batch_id"],
                "phase": phase,
                "run_id": result.run_id,
                "result_status": result.status,
                "summary": result.summary,
            }
            write_report(self.repo_root, f"pilot_{batch['batch_id']}_research.json", report)
            return report

        return {"status": "UNSUPPORTED_PHASE", "phase": phase}
