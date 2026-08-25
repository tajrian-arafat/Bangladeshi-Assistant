"""Deployment and publication safety gates."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEPLOYMENT_PATTERNS = [
    re.compile(r"\bnpx\s+convex\s+deploy\b", re.I),
    re.compile(r"\bvercel\s+--prod\b", re.I),
    re.compile(r"\brender\s+deploy\b", re.I),
    re.compile(r"\bkubectl\s+apply\b", re.I),
    re.compile(r"\bterraform\s+apply\b", re.I),
    re.compile(r"\bdocker\s+push\b", re.I),
    re.compile(r"\bgit\s+push\s+.*main\b", re.I),
    re.compile(r"\bgh\s+pr\s+merge\b", re.I),
    re.compile(r"\bproduction\b", re.I),
    re.compile(r"\bdeploy\s+to\s+prod", re.I),
]

PUBLICATION_SCRIPT = re.compile(r"publish_verified_knowledge\.py.*--publish", re.I)


@dataclass
class GateResult:
    passed: bool
    gate_id: str
    message: str
    severity: str = "INFO"


class GateEngine:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.automation_dir = repo_root / ".automation"
        self.gates_path = self.automation_dir / "gates.yaml"

    def read_deployment_lock(self) -> bool:
        lock_path = self.automation_dir / "deployment.lock"
        if not lock_path.exists():
            return False
        raw = lock_path.read_text(encoding="utf-8").strip().lower()
        return raw in {"true", "1", "yes", "allowed"}

    def assert_deployment_locked(self) -> GateResult:
        if self.read_deployment_lock():
            return GateResult(False, "deployment_lock", "Deployment is ALLOWED — unexpected unlock", "CRITICAL")
        return GateResult(True, "deployment_lock", "Deployment hard lock active (deployment_allowed=false)")

    def check_shell_command(self, command: str) -> GateResult:
        if self.read_deployment_lock():
            return GateResult(True, "shell_command", "Deployment unlocked — shell not blocked by lock")
        for pattern in DEPLOYMENT_PATTERNS:
            if pattern.search(command):
                return GateResult(
                    False,
                    "shell_deployment_block",
                    f"Blocked deployment/production command: {pattern.pattern}",
                    "CRITICAL",
                )
        return GateResult(True, "shell_command", "Command permitted under deployment lock")

    def check_publication_command(self, command: str) -> GateResult:
        if PUBLICATION_SCRIPT.search(command):
            state_path = self.automation_dir / "project_state.json"
            if state_path.exists():
                state = json.loads(state_path.read_text(encoding="utf-8"))
                if state.get("workflow_status") in {"BLOCKED", "HUMAN_APPROVAL_REQUIRED"}:
                    return GateResult(
                        False,
                        "publication_block",
                        "Publication blocked while workflow requires human approval",
                        "CRITICAL",
                    )
        return GateResult(True, "publication_command", "Publication command check passed")

    def validate_regression_metrics(self, metrics: dict[str, Any]) -> GateResult:
        failures: list[str] = []
        if metrics.get("hallucinations", 0) > 0:
            failures.append("hallucinations > 0")
        if metrics.get("citation_failures", 0) > 0:
            failures.append("citation_failures > 0")
        if metrics.get("batch_01_pass_pct", 100) < 100:
            failures.append("Batch 1 regression")
        if metrics.get("passport_pass_pct", 100) < 100:
            failures.append("Passport regression")
        if metrics.get("batch_02b_pass_pct", 100) < 100:
            failures.append("Batch 2B regression")
        if metrics.get("routing_pass_pct", 100) < 100:
            failures.append("Routing regression")
        if metrics.get("pytest_failed", 0) > 0:
            failures.append("pytest failures")
        if failures:
            return GateResult(False, "regression_gate", "; ".join(failures), "CRITICAL")
        return GateResult(True, "regression_gate", "All regression gates passed")

    def validate_phase_result_gates(self, result: dict[str, Any]) -> list[GateResult]:
        results: list[GateResult] = []
        if result.get("hallucinations", 0) > 0:
            results.append(GateResult(False, "no_hallucinations", "Hallucinations detected", "CRITICAL"))
        else:
            results.append(GateResult(True, "no_hallucinations", "Zero hallucinations"))
        if result.get("citation_failures", 0) > 0:
            results.append(GateResult(False, "no_citation_failures", "Citation failures detected", "CRITICAL"))
        else:
            results.append(GateResult(True, "no_citation_failures", "Zero citation failures"))
        if result.get("critical_conflicts", 0) > 0 and result.get("phase") == "PUBLICATION":
            results.append(
                GateResult(False, "no_critical_conflicts", "Critical conflicts block publication", "CRITICAL")
            )
        else:
            results.append(GateResult(True, "no_critical_conflicts", "No blocking critical conflicts"))
        if result.get("regressions", 0) > 0:
            results.append(GateResult(False, "no_regressions", "Regressions detected", "CRITICAL"))
        else:
            results.append(GateResult(True, "no_regressions", "No regressions"))
        return results

    def load_gate_config(self) -> dict[str, Any]:
        if not self.gates_path.exists():
            return {}
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError:
            return {"note": "PyYAML not installed; using built-in gates only"}
        return yaml.safe_load(self.gates_path.read_text(encoding="utf-8")) or {}
