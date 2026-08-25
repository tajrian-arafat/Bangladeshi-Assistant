"""Quality gate tests."""

from __future__ import annotations

from pathlib import Path

from automation.orchestrator.gate_engine import GateEngine


REPO = Path(__file__).resolve().parents[2]


def test_deployment_lock_blocks_deploy() -> None:
    engine = GateEngine(REPO)
    lock_path = REPO / ".automation" / "deployment.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("false\n")
    result = engine.check_shell_command("npx convex deploy")
    assert not result.passed


def test_regression_gate_fails_on_hallucination() -> None:
    engine = GateEngine(REPO)
    result = engine.validate_regression_metrics({"hallucinations": 1})
    assert not result.passed


def test_regression_gate_passes_baseline() -> None:
    engine = GateEngine(REPO)
    result = engine.validate_regression_metrics(
        {
            "hallucinations": 0,
            "citation_failures": 0,
            "batch_01_pass_pct": 100,
            "passport_pass_pct": 100,
            "batch_02b_pass_pct": 100,
            "routing_pass_pct": 100,
            "pytest_failed": 0,
        }
    )
    assert result.passed
