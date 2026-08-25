"""Execute workflow phases via deterministic scripts (local/dev only)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.phase_completion import (
    batch_slug,
    check_research_complete,
    phase_artifacts_complete,
    raw_research_dir,
)
from automation.schemas.result import PhaseResult


class PhaseExecutor:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.python = sys.executable

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _batch_script_prefix(self, slug: str) -> str:
        """Map batch slug to script prefix (batch-03a-x -> batch03a_x)."""
        if slug.startswith("batch-"):
            return slug.replace("batch-", "batch", 1).replace("-", "_")
        return slug.replace("-", "_")

    def _run_script(self, script: str, *args: str, timeout: int = 600) -> tuple[int, str]:
        cmd = [self.python, str(self.repo_root / "scripts" / script), *args]
        proc = subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, output

    def _run_cmd(self, cmd: list[str], cwd: Path | None = None, timeout: int = 600) -> tuple[int, str]:
        proc = subprocess.run(
            cmd,
            cwd=cwd or self.repo_root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, output

    def execute_research(
        self,
        *,
        run_id: str,
        batch: dict[str, Any],
        batch_manager: BatchManager,
    ) -> PhaseResult:
        started = self._now()
        slug = batch_slug(batch)
        report = check_research_complete(self.repo_root, batch)
        artifacts: list[str] = []

        if not report.complete:
            prefix = self._batch_script_prefix(slug)
            gen_script = f"generate_{prefix}_research_artifacts.py"
            gen_path = self.repo_root / "scripts" / gen_script
            if gen_path.exists():
                code, output = self._run_script(gen_script)
                if code != 0:
                    return PhaseResult(
                        run_id=run_id,
                        batch_id=batch["batch_id"],
                        phase="RESEARCH",
                        status="FAILED",
                        started_at=started,
                        completed_at=self._now(),
                        services_total=len(batch.get("service_ids") or []),
                        summary=f"Research generator failed: {output[-500:]}",
                        recommended_next_phase="RESEARCH",
                        idempotency_key=f"{batch['batch_id']}:RESEARCH:{run_id}",
                    )
            else:
                batch_manager.setup_research_artifacts(batch)

        report = check_research_complete(self.repo_root, batch)
        raw = raw_research_dir(self.repo_root, batch)
        for p in raw.rglob("*.json"):
            artifacts.append(str(p.relative_to(self.repo_root)))

        meta = {}
        if (raw / "metadata.json").exists():
            meta = json.loads((raw / "metadata.json").read_text(encoding="utf-8"))

        if not report.complete:
            return PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase="RESEARCH",
                status="PARTIAL",
                started_at=started,
                completed_at=self._now(),
                services_total=len(batch.get("service_ids") or []),
                services_processed=int(meta.get("services_researched") or 0),
                claims_total=int(meta.get("claims_total") or 0),
                artifacts=artifacts,
                summary=f"Research incomplete: {len(report.missing)} missing artifacts",
                recommended_next_phase="RESEARCH",
                metadata={"missing": report.missing[:10]},
                idempotency_key=f"{batch['batch_id']}:RESEARCH:{run_id}",
            )

        return PhaseResult(
            run_id=run_id,
            batch_id=batch["batch_id"],
            phase="RESEARCH",
            status="SUCCESS",
            started_at=started,
            completed_at=self._now(),
            services_total=int(meta.get("services_in_scope") or len(batch.get("service_ids") or [])),
            services_processed=int(meta.get("services_researched") or 0),
            claims_total=int(meta.get("claims_total") or 0),
            knowledge_gaps=int(meta.get("knowledge_gaps") or 0),
            conflicting=int(meta.get("conflicts") or 0),
            artifacts=artifacts,
            summary=f"Research complete for {batch['batch_id']}: {meta.get('claims_total', 0)} claims",
            recommended_next_phase="VERIFICATION",
            idempotency_key=f"{batch['batch_id']}:RESEARCH:complete",
        )

    def execute_verification(self, *, run_id: str, batch: dict[str, Any]) -> PhaseResult:
        started = self._now()
        slug = batch_slug(batch)
        prefix = self._batch_script_prefix(slug)
        script = f"verify_{prefix}_claims.py"
        script_path = self.repo_root / "scripts" / script
        if not script_path.exists():
            return PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase="VERIFICATION",
                status="FAILED",
                started_at=started,
                completed_at=self._now(),
                summary=f"Missing verification script: {script}",
                recommended_next_phase="VERIFICATION",
                idempotency_key=f"{batch['batch_id']}:VERIFICATION:{run_id}",
            )

        code, output = self._run_script(script, timeout=900)
        verify_path = self.repo_root / "data" / "research" / "verification" / slug / "claims_verification.json"
        summary_path = self.repo_root / "data" / "research" / "verification" / slug / "summary.json"
        metrics: dict[str, Any] = {}
        if summary_path.exists():
            metrics = json.loads(summary_path.read_text(encoding="utf-8"))
        elif verify_path.exists():
            metrics = json.loads(verify_path.read_text(encoding="utf-8"))

        summary_block = metrics.get("summary") if isinstance(metrics.get("summary"), dict) else metrics
        status_counts = summary_block.get("status_counts") or {}
        verified = int(summary_block.get("verified") or status_counts.get("VERIFIED") or 0)
        partial = int(summary_block.get("partially_verified") or status_counts.get("PARTIALLY_VERIFIED") or 0)
        unverified = int(summary_block.get("unverified") or status_counts.get("UNVERIFIED") or 0)
        conflicting = int(summary_block.get("conflicting") or status_counts.get("CONFLICTING") or 0)
        critical = int(summary_block.get("critical_conflicts") or 0)
        gaps = int(
            summary_block.get("knowledge_gaps")
            or summary_block.get("knowledge_gaps_open")
            or summary_block.get("gaps")
            or 0
        )
        claims_total = int(summary_block.get("claims_total") or summary_block.get("total_claims") or 0)

        if code != 0:
            return PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase="VERIFICATION",
                status="FAILED",
                started_at=started,
                completed_at=self._now(),
                claims_total=claims_total,
                verified=verified,
                partial=partial,
                unverified=unverified,
                conflicting=conflicting,
                critical_conflicts=critical,
                knowledge_gaps=gaps,
                summary=f"Verification script failed: {output[-500:]}",
                recommended_next_phase="VERIFICATION",
                idempotency_key=f"{batch['batch_id']}:VERIFICATION:{run_id}",
            )

        normalize_script = f"normalize_{prefix}_to_staging.py"
        if (self.repo_root / "scripts" / normalize_script).exists():
            norm_code, norm_out = self._run_script(normalize_script)
            if norm_code != 0:
                return PhaseResult(
                    run_id=run_id,
                    batch_id=batch["batch_id"],
                    phase="VERIFICATION",
                    status="FAILED",
                    started_at=started,
                    completed_at=self._now(),
                    summary=f"Staging normalization failed: {norm_out[-500:]}",
                    recommended_next_phase="VERIFICATION",
                    idempotency_key=f"{batch['batch_id']}:VERIFICATION:{run_id}",
                )

        if critical > 0:
            return PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase="VERIFICATION",
                status="ESCALATED",
                started_at=started,
                completed_at=self._now(),
                claims_total=claims_total,
                verified=verified,
                partial=partial,
                unverified=unverified,
                conflicting=conflicting,
                critical_conflicts=critical,
                knowledge_gaps=gaps,
                requires_escalation=True,
                summary=f"Critical conflicts ({critical}) require human approval",
                recommended_next_phase="HUMAN_APPROVAL_REQUIRED",
                idempotency_key=f"{batch['batch_id']}:VERIFICATION:{run_id}",
            )

        next_phase = "GAP_CLOSURE" if gaps > 0 else "PUBLICATION"
        return PhaseResult(
            run_id=run_id,
            batch_id=batch["batch_id"],
            phase="VERIFICATION",
            status="SUCCESS",
            started_at=started,
            completed_at=self._now(),
            claims_total=claims_total,
            verified=verified,
            partial=partial,
            unverified=unverified,
            conflicting=conflicting,
            critical_conflicts=critical,
            knowledge_gaps=gaps,
            artifacts=[str(verify_path.relative_to(self.repo_root))],
            summary=f"Verification complete: {verified} verified, {gaps} gaps",
            recommended_next_phase=next_phase,
            idempotency_key=f"{batch['batch_id']}:VERIFICATION:complete",
        )

    def execute_gap_closure(self, *, run_id: str, batch: dict[str, Any]) -> PhaseResult:
        started = self._now()
        slug = batch_slug(batch)
        prefix = self._batch_script_prefix(slug)
        script = f"generate_{prefix}_gap_closure.py"
        script_path = self.repo_root / "scripts" / script
        if script_path.exists():
            code, output = self._run_script(script)
            if code != 0:
                return PhaseResult(
                    run_id=run_id,
                    batch_id=batch["batch_id"],
                    phase="GAP_CLOSURE",
                    status="FAILED",
                    started_at=started,
                    completed_at=self._now(),
                    summary=f"Gap closure failed: {output[-500:]}",
                    recommended_next_phase="GAP_CLOSURE",
                    idempotency_key=f"{batch['batch_id']}:GAP_CLOSURE:{run_id}",
                )
        # Re-run verification after gap closure
        return self.execute_verification(run_id=run_id, batch=batch)

    def execute_publication(self, *, run_id: str, batch: dict[str, Any]) -> PhaseResult:
        started = self._now()
        slug = batch_slug(batch)
        batch_arg = slug  # e.g. batch-03a-brta-driving-licence

        code_dry, out_dry = self._run_cmd(
            [self.python, "scripts/publish_verified_knowledge.py", "--batch", batch_arg, "--dry-run"],
            timeout=300,
        )
        if code_dry != 0:
            return PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase="PUBLICATION",
                status="BLOCKED",
                started_at=started,
                completed_at=self._now(),
                summary=f"Publication dry-run blocked: {out_dry[-500:]}",
                recommended_next_phase="PUBLICATION",
                idempotency_key=f"{batch['batch_id']}:PUBLICATION:{run_id}",
            )

        code_pub, out_pub = self._run_cmd(
            [
                self.python,
                "scripts/publish_verified_knowledge.py",
                "--batch",
                batch_arg,
                "--publish",
                "--commit",
            ],
            timeout=300,
        )
        report_path = self.repo_root / "docs" / "research" / f"{slug}-publication-report.md"
        if code_pub != 0:
            return PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase="PUBLICATION",
                status="FAILED",
                started_at=started,
                completed_at=self._now(),
                summary=f"Local publication failed: {out_pub[-500:]}",
                recommended_next_phase="PUBLICATION",
                idempotency_key=f"{batch['batch_id']}:PUBLICATION:{run_id}",
            )

        artifacts = [str(report_path.relative_to(self.repo_root))] if report_path.exists() else []
        candidate_report_path = self.repo_root / "data" / "audit" / f"seed-candidates-{batch_arg}.json"
        detect_code, detect_out = self._run_cmd(
            [
                self.python,
                "scripts/detect_legacy_seed_candidates.py",
                "--batch",
                batch_arg,
                "--record",
            ],
            timeout=120,
        )
        requires_seed_approval = detect_code == 2
        if candidate_report_path.exists():
            artifacts.append(str(candidate_report_path.relative_to(self.repo_root)))

        if requires_seed_approval:
            return PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase="PUBLICATION",
                status="SUCCESS",
                started_at=started,
                completed_at=self._now(),
                artifacts=artifacts,
                requires_escalation=True,
                recommended_next_phase="HUMAN_APPROVAL_REQUIRED",
                summary=(
                    f"Publication complete for {batch_arg}; "
                    "legacy seed replacement candidates require explicit human approval"
                ),
                metadata={"seed_replacement_detect": detect_out[-2000:]},
                idempotency_key=f"{batch['batch_id']}:PUBLICATION:complete",
            )

        return PhaseResult(
            run_id=run_id,
            batch_id=batch["batch_id"],
            phase="PUBLICATION",
            status="SUCCESS",
            started_at=started,
            completed_at=self._now(),
            artifacts=artifacts,
            summary=f"Local publication complete for {batch_arg}",
            recommended_next_phase="E2E",
            idempotency_key=f"{batch['batch_id']}:PUBLICATION:complete",
        )

    def execute_e2e(self, *, run_id: str, batch: dict[str, Any]) -> PhaseResult:
        started = self._now()
        slug = batch_slug(batch)
        prefix = self._batch_script_prefix(slug)
        script = f"evaluate_{prefix}_e2e.py"
        script_path = self.repo_root / "scripts" / script
        if not script_path.exists():
            return PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase="E2E",
                status="FAILED",
                started_at=started,
                completed_at=self._now(),
                summary=f"Missing E2E script: {script}",
                idempotency_key=f"{batch['batch_id']}:E2E:{run_id}",
            )

        code, output = self._run_script(script, timeout=900)
        summary_path = self.repo_root / "data" / "evaluation" / slug / "summary.json"
        metrics: dict[str, Any] = {}
        if summary_path.exists():
            metrics = json.loads(summary_path.read_text(encoding="utf-8"))

        total = int(metrics.get("total") or metrics.get("queries_total") or 0)
        passed = int(metrics.get("passed") or metrics.get("queries_passed") or 0)
        failed = int(metrics.get("failed") or metrics.get("queries_failed") or 0)
        hallucinations = int(metrics.get("hallucinations") or 0)
        citation_failures = int(metrics.get("citation_failures") or 0)

        status = "SUCCESS" if code == 0 and hallucinations == 0 and citation_failures == 0 else "BLOCKED"
        if code != 0:
            status = "FAILED"

        return PhaseResult(
            run_id=run_id,
            batch_id=batch["batch_id"],
            phase="E2E",
            status=status,
            started_at=started,
            completed_at=self._now(),
            e2e_total=total,
            e2e_passed=passed,
            e2e_failed=failed,
            hallucinations=hallucinations,
            citation_failures=citation_failures,
            artifacts=[str(summary_path.relative_to(self.repo_root))] if summary_path.exists() else [],
            summary=f"E2E: {passed}/{total} passed, hallucinations={hallucinations}",
            recommended_next_phase="REGRESSION" if status == "SUCCESS" else "E2E",
            idempotency_key=f"{batch['batch_id']}:E2E:complete",
        )

    def execute_regression(self, *, run_id: str, batch: dict[str, Any]) -> PhaseResult:
        started = self._now()
        metrics: dict[str, Any] = {
            "hallucinations": 0,
            "citation_failures": 0,
            "batch_01_pass_pct": 100,
            "passport_pass_pct": 100,
            "batch_02b_pass_pct": 100,
            "routing_pass_pct": 100,
            "pytest_failed": 0,
        }
        failures: list[str] = []

        suites = [
            ("evaluate_batch01_e2e.py", "batch_01_pass_pct", "data/evaluation/batch-01/summary.json", "pass_pct"),
            ("evaluate_batch02a_e2e.py", "passport_pass_pct", "data/evaluation/batch-02a-passport/summary.json", "pass_pct"),
            ("evaluate_batch02b_e2e.py", "batch_02b_pass_pct", "data/evaluation/batch-02b-police-immigration/summary.json", "pass_pct"),
            ("evaluate_service_routing.py", "routing_pass_pct", "data/evaluation/service-routing/summary.json", "pass_pct"),
            ("evaluate_cross_domain_hardening.py", None, "data/evaluation/cross-domain-hardening/summary.json", "pass_pct"),
        ]

        for script, metric_key, summary_rel, pct_field in suites:
            code, _ = self._run_script(script, timeout=900)
            summary_path = self.repo_root / summary_rel
            if summary_path.exists():
                s = json.loads(summary_path.read_text(encoding="utf-8"))
                pct = float(s.get(pct_field) or s.get("pass_pct") or (100 if code == 0 else 0))
                if metric_key:
                    metrics[metric_key] = pct
                if pct < 100:
                    failures.append(f"{script}: {pct}%")
            elif code != 0:
                failures.append(script)

        pytest_code, pytest_out = self._run_cmd(
            [str(self.repo_root / "backend" / ".venv" / "bin" / "pytest"), "tests/", "-q"],
            cwd=self.repo_root / "backend",
            timeout=600,
        )
        if pytest_code != 0:
            metrics["pytest_failed"] = 1
            failures.append("pytest")

        report_path = self.repo_root / ".automation" / "reports" / f"regression_{batch['batch_id']}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps({"metrics": metrics, "failures": failures}, indent=2) + "\n")

        regressions = len(failures)
        status = "SUCCESS" if regressions == 0 else "BLOCKED"
        return PhaseResult(
            run_id=run_id,
            batch_id=batch["batch_id"],
            phase="REGRESSION",
            status=status,
            started_at=started,
            completed_at=self._now(),
            regressions=regressions,
            hallucinations=int(metrics.get("hallucinations") or 0),
            citation_failures=int(metrics.get("citation_failures") or 0),
            artifacts=[str(report_path.relative_to(self.repo_root))],
            summary=f"Regression: {regressions} failures" if failures else "All regression suites passed",
            recommended_next_phase="" if status == "SUCCESS" else "REGRESSION",
            metadata={"metrics": metrics, "failures": failures},
            idempotency_key=f"{batch['batch_id']}:REGRESSION:complete",
        )

    def execute_phase(
        self,
        *,
        run_id: str,
        batch: dict[str, Any],
        phase: str,
        batch_manager: BatchManager,
    ) -> PhaseResult:
        executors = {
            "RESEARCH": lambda: self.execute_research(run_id=run_id, batch=batch, batch_manager=batch_manager),
            "VERIFICATION": lambda: self.execute_verification(run_id=run_id, batch=batch),
            "GAP_CLOSURE": lambda: self.execute_gap_closure(run_id=run_id, batch=batch),
            "PUBLICATION": lambda: self.execute_publication(run_id=run_id, batch=batch),
            "E2E": lambda: self.execute_e2e(run_id=run_id, batch=batch),
            "REGRESSION": lambda: self.execute_regression(run_id=run_id, batch=batch),
        }
        fn = executors.get(phase)
        if not fn:
            return PhaseResult(
                run_id=run_id,
                batch_id=batch["batch_id"],
                phase=phase,
                status="FAILED",
                started_at=self._now(),
                completed_at=self._now(),
                summary=f"Unsupported phase: {phase}",
                idempotency_key=f"{batch['batch_id']}:{phase}:{run_id}",
            )
        return fn()
