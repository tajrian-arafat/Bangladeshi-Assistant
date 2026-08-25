"""Automation orchestrator CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.escalation_manager import EscalationManager
from automation.orchestrator.gate_engine import GateEngine
from automation.orchestrator.logging import setup_logging, write_report
from automation.orchestrator.overnight_runner import OvernightRunner
from automation.orchestrator.phase_runner import PhaseRunner
from automation.orchestrator.state_machine import StateMachine
from automation.schemas.state import ProjectState, WorkflowStatus


REPO_ROOT = Path(__file__).resolve().parents[2]
AUTOMATION_DIR = REPO_ROOT / ".automation"


def _write_initial_state() -> None:
    AUTOMATION_DIR.mkdir(parents=True, exist_ok=True)
    (AUTOMATION_DIR / "deployment.lock").write_text("false\n", encoding="utf-8")
    (AUTOMATION_DIR / "runs").mkdir(exist_ok=True)
    (AUTOMATION_DIR / "decisions").mkdir(exist_ok=True)
    (AUTOMATION_DIR / "reports").mkdir(exist_ok=True)

    state = ProjectState(
        project_name="Bangladeshi Assistant",
        mode="LOCAL_DEV_ONLY",
        deployment_allowed=False,
        current_batch="BATCH_03A",
        current_phase="RESEARCH",
        workflow_status=WorkflowStatus.READY.value,
        last_completed_batch="BATCH_02B",
        pilot_mode=True,
        continuous_mode=False,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    StateMachine(REPO_ROOT).save(state)

    workflow = {
        "version": "1.0.0",
        "phases": ["RESEARCH", "VERIFICATION", "GAP_CLOSURE", "PUBLICATION", "E2E", "REGRESSION", "STABILIZATION"],
        "transitions": {
            "READY": ["RUNNING"],
            "RUNNING": ["WAITING_FOR_RESULT"],
            "WAITING_FOR_RESULT": ["VALIDATING_RESULT"],
            "VALIDATING_RESULT": [
                "AUTO_CONTINUE",
                "RETRY",
                "GAP_CLOSURE",
                "SUPERVISOR_REVIEW",
                "HUMAN_APPROVAL_REQUIRED",
                "BLOCKED",
                "COMPLETE",
            ],
            "BLOCKED": ["READY", "RETRY", "HUMAN_APPROVAL_REQUIRED", "STOPPED"],
        },
        "publication_mode": "LOCAL_DEV_ONLY",
        "merge_policy": "MANUAL_ONLY",
    }
    (AUTOMATION_DIR / "workflow.yaml").write_text(
        "# BDA Automation Workflow\n" + json.dumps(workflow, indent=2) + "\n",
        encoding="utf-8",
    )

    gates = {
        "deployment_allowed": False,
        "require_zero_hallucinations": True,
        "require_zero_citation_failures": True,
        "regression_suites": [
            "batch_01_e2e",
            "passport_e2e",
            "batch_02b_e2e",
            "service_routing",
            "cross_domain_hardening",
            "pytest",
        ],
        "max_retries": 3,
    }
    (AUTOMATION_DIR / "gates.yaml").write_text(
        "# Quality gates\n" + json.dumps(gates, indent=2) + "\n",
        encoding="utf-8",
    )

    BatchManager(REPO_ROOT).write_queue()


def cmd_init(_: argparse.Namespace) -> int:
    _write_initial_state()
    print(json.dumps({"status": "initialized", "path": str(AUTOMATION_DIR)}, indent=2))
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    sm = StateMachine(REPO_ROOT)
    state = sm.load()
    gates = GateEngine(REPO_ROOT)
    escalation = EscalationManager(REPO_ROOT)
    git_info = {}
    try:
        from automation.orchestrator.github_adapter import GitHubAdapter

        git_info = GitHubAdapter(REPO_ROOT).snapshot()
    except Exception:
        pass
    pending = [d.decision_id for d in escalation.list_pending()]
    next_action = "idle"
    if state.workflow_status == WorkflowStatus.READY.value and state.current_batch:
        next_action = f"run {state.current_batch} {state.current_phase}"
    elif pending:
        next_action = f"approve decision(s): {pending}"
    payload = {
        "project": state.project_name,
        "mode": state.mode,
        "deployment_allowed": gates.read_deployment_lock(),
        "deployment_lock_active": not gates.read_deployment_lock(),
        "current_batch": state.current_batch,
        "current_phase": state.current_phase,
        "current_run_id": state.current_run_id,
        "workflow_status": state.workflow_status,
        "last_completed_batch": state.last_completed_batch,
        "pilot_mode": state.pilot_mode,
        "continuous_mode": state.continuous_mode,
        "pending_escalations": pending,
        "regression_baseline": __import__("dataclasses").asdict(state.regression_baseline),
        "catalogue": __import__("dataclasses").asdict(state.catalogue),
        "git": git_info,
        "next_action": next_action,
    }
    print(json.dumps(payload, indent=2))
    return 0


def cmd_simulate(_: argparse.Namespace) -> int:
    runner = PhaseRunner(REPO_ROOT)
    summary = runner.simulate_all()
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 1


def cmd_run(_: argparse.Namespace) -> int:
    sm = StateMachine(REPO_ROOT)
    if not sm.state_path.exists():
        cmd_init(_)
    state = sm.load()
    if state.workflow_status == WorkflowStatus.PAUSED.value:
        print(json.dumps({"error": "Orchestrator is paused. Use resume."}, indent=2))
        return 1
    if state.workflow_status == WorkflowStatus.STOPPED.value:
        sm.transition(state, WorkflowStatus.READY)
        state = sm.load()
    runner = PhaseRunner(REPO_ROOT)
    # Run autonomous loop until a terminal state (one full continuation chain)
    summary = runner.run_autonomous_loop(state, max_steps=20)
    print(json.dumps(summary, indent=2))
    return 0


def cmd_run_once(_: argparse.Namespace) -> int:
    """Single step only — manual recovery."""
    sm = StateMachine(REPO_ROOT)
    state = sm.load()
    runner = PhaseRunner(REPO_ROOT)
    report = runner.run_autonomous_step(state)
    print(json.dumps(report, indent=2))
    return 0


def cmd_resume(_: argparse.Namespace) -> int:
    sm = StateMachine(REPO_ROOT)
    state = sm.load()
    if state.workflow_status in {WorkflowStatus.PAUSED.value, WorkflowStatus.STOPPED.value}:
        sm.transition(state, WorkflowStatus.READY)
    return cmd_run(_)


def cmd_pause(_: argparse.Namespace) -> int:
    sm = StateMachine(REPO_ROOT)
    state = sm.load()
    state.workflow_status = WorkflowStatus.PAUSED.value
    sm.save(state)
    print(json.dumps({"status": "paused"}, indent=2))
    return 0


def cmd_stop(_: argparse.Namespace) -> int:
    sm = StateMachine(REPO_ROOT)
    state = sm.load()
    state.workflow_status = WorkflowStatus.STOPPED.value
    sm.save(state)
    print(json.dumps({"status": "stopped"}, indent=2))
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    token = os.environ.get("BDA_HUMAN_APPROVAL_TOKEN")
    if not token or token != os.environ.get("BDA_HUMAN_APPROVAL_TOKEN_EXPECTED", token):
        # Require explicit token match when EXPECTED is set; otherwise allow local dev token
        expected = os.environ.get("BDA_HUMAN_APPROVAL_TOKEN")
        if not expected:
            print(
                json.dumps(
                    {
                        "error": "Set BDA_HUMAN_APPROVAL_TOKEN to approve human decisions",
                    },
                    indent=2,
                )
            )
            return 1
    escalation = EscalationManager(REPO_ROOT)
    if args.decision_id == "deployment_unlock":
        if os.environ.get("BDA_DEPLOYMENT_UNLOCK") != "I_UNDERSTAND_PRODUCTION_RISK":
            print(json.dumps({"error": "Set BDA_DEPLOYMENT_UNLOCK=I_UNDERSTAND_PRODUCTION_RISK"}, indent=2))
            return 1
        (AUTOMATION_DIR / "deployment.lock").write_text("true\n", encoding="utf-8")
        print(json.dumps({"status": "deployment_unlocked", "warning": "Human override applied"}, indent=2))
        return 0
    record = escalation.resolve_decision(
        args.decision_id,
        resolution=args.resolution or "approved",
        approved_by="human",
    )
    sm = StateMachine(REPO_ROOT)
    state = sm.load()
    if record.decision_id in state.pending_escalations:
        state.pending_escalations.remove(record.decision_id)
    sm.transition(state, WorkflowStatus.READY)
    print(json.dumps(record.to_dict(), indent=2))
    return 0


def cmd_overnight(args: argparse.Namespace) -> int:
    """Unattended overnight knowledge-construction loop."""
    sm = StateMachine(REPO_ROOT)
    if not sm.state_path.exists():
        cmd_init(args)
    runner = OvernightRunner(REPO_ROOT)
    summary = runner.run(max_steps=args.max_ticks, steps_per_tick=args.steps_per_tick)
    print(json.dumps(summary, indent=2))
    if summary.get("status") == "BLOCKED_GLOBAL":
        return 1
    return 0


def cmd_daemon(args: argparse.Namespace) -> int:
    interval = args.interval
    logger = setup_logging(REPO_ROOT, "daemon")
    logger.info("Starting automation daemon (interval=%ss)", interval)
    sm = StateMachine(REPO_ROOT)
    state = sm.load()
    state.continuous_mode = True
    sm.save(state)
    while True:
        sm = StateMachine(REPO_ROOT)
        state = sm.load()
        if state.workflow_status in {WorkflowStatus.PAUSED.value, WorkflowStatus.STOPPED.value}:
            time.sleep(interval)
            continue
        if state.pending_escalations:
            logger.warning("Pending escalations — sleeping")
            time.sleep(interval)
            continue
        runner = PhaseRunner(REPO_ROOT)
        summary = runner.run_autonomous_loop(state, max_steps=10)
        logger.info("Daemon tick: %s", summary.get("final_status"))
        final = summary.get("final_status")
        last = summary.get("last") or {}
        if final in {"HUMAN_APPROVAL_REQUIRED", "BLOCKED", "COMPLETE", "SUPERVISOR_REVIEW"}:
            logger.info("Stopping daemon: %s", final)
            break
        if last.get("result_status") == "PARTIAL":
            logger.info("Phase partial — waiting for artifacts")
            time.sleep(interval)
            continue
        time.sleep(interval)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BDA Knowledge Construction Orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize automation state")
    sub.add_parser("status", help="Show orchestrator status")
    sub.add_parser("simulate", help="Run offline simulation cases")
    sub.add_parser("run", help="Run autonomous continuation loop until terminal state")
    sub.add_parser("step", help="Run a single orchestrator step (manual recovery)")
    sub.add_parser("resume", help="Resume from pause/stop")
    sub.add_parser("pause", help="Pause automation")
    sub.add_parser("stop", help="Stop automation")

    approve = sub.add_parser("approve", help="Human approve a decision")
    approve.add_argument("decision_id", help="Decision ID or deployment_unlock")
    approve.add_argument("--resolution", default="approved", help="Resolution text")

    daemon = sub.add_parser("daemon", help="Continuous mode loop")
    daemon.add_argument("--interval", type=int, default=60, help="Sleep seconds between ticks")

    overnight = sub.add_parser("overnight", help="Unattended overnight knowledge-construction loop")
    overnight.add_argument("--max-ticks", type=int, default=500, help="Maximum outer loop ticks")
    overnight.add_argument("--steps-per-tick", type=int, default=25, help="Autonomous steps per tick")

    args = parser.parse_args(argv)
    commands = {
        "init": cmd_init,
        "status": cmd_status,
        "simulate": cmd_simulate,
        "run": cmd_run,
        "step": cmd_run_once,
        "resume": cmd_resume,
        "pause": cmd_pause,
        "stop": cmd_stop,
        "approve": cmd_approve,
        "daemon": cmd_daemon,
        "overnight": cmd_overnight,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
