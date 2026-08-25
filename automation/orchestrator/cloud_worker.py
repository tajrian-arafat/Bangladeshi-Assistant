"""In-process cloud worker — executes task specs without batch-specific scripts."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.gap_closure_builder import GapClosureBuilder
from automation.orchestrator.phase_completion import batch_slug, check_research_complete, check_batch_research_quality, phase_artifacts_complete
from automation.orchestrator.research_builder import ResearchBuilder
from automation.orchestrator.service_research_builder import ServiceResearchBuilder, PILOT_SERVICE_IDS
from automation.orchestrator.task_factory import CloudTaskSpec
from automation.orchestrator.verification_builder import VerificationBuilder
from automation.schemas.result import PhaseResult


AGENT_PHASES = frozenset({"RESEARCH", "VERIFICATION", "GAP_CLOSURE", "PUBLICATION", "E2E"})


class CloudWorker:
    """Execute cloud task specs synchronously inside a Cursor Cloud Agent VM."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.batch_manager = BatchManager(repo_root)
        self.research_builder = ResearchBuilder(repo_root)
        self.service_research_builder = ServiceResearchBuilder(repo_root)
        self.verification_builder = VerificationBuilder(repo_root)
        self.gap_closure_builder = GapClosureBuilder(repo_root)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _batch_script_prefix(self, slug: str) -> str:
        if slug.startswith("batch-"):
            return slug.replace("batch-", "batch", 1).replace("-", "_")
        return slug.replace("-", "_")

    def execute(self, task: CloudTaskSpec, batch: dict[str, Any]) -> PhaseResult:
        started = self._now()
        phase = task.phase

        if phase == "RESEARCH":
            return self._execute_research(task, batch, started)
        if phase == "VERIFICATION":
            return self._execute_verification(task, batch, started)
        if phase == "GAP_CLOSURE":
            return self._execute_gap_closure(task, batch, started)
        if phase == "E2E":
            return self._execute_via_legacy_or_partial(task, batch, started)
        if phase in AGENT_PHASES:
            return self._execute_via_legacy_or_partial(task, batch, started)
        return PhaseResult(
            run_id=task.run_id,
            batch_id=task.batch_id,
            phase=phase,
            status="FAILED",
            started_at=started,
            completed_at=self._now(),
            summary=f"Unsupported cloud worker phase: {phase}",
            idempotency_key=f"{task.batch_id}:{phase}:{task.run_id}",
        )

    def _execute_research(self, task: CloudTaskSpec, batch: dict[str, Any], started: str) -> PhaseResult:
        service_ids = list(batch.get("service_ids") or [])
        pilot_ids = [sid for sid in service_ids if sid in PILOT_SERVICE_IDS]
        if pilot_ids and set(pilot_ids) == set(service_ids):
            for sid in pilot_ids:
                self.service_research_builder.build_service_research(sid)

        report = check_research_complete(self.repo_root, batch)
        if not report.complete:
            self.research_builder.build_batch_research(batch)
            report = check_research_complete(self.repo_root, batch)

        quality = check_batch_research_quality(self.repo_root, batch)
        meta_path = self.repo_root / "data" / "research" / "raw" / batch_slug(batch) / "metadata.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

        if not report.complete or not quality.complete:
            return PhaseResult(
                run_id=task.run_id,
                batch_id=task.batch_id,
                phase="RESEARCH",
                status="PARTIAL",
                started_at=started,
                completed_at=self._now(),
                services_total=len(service_ids),
                services_processed=int(meta.get("services_researched") or 0),
                claims_total=int(meta.get("claims_total") or 0),
                knowledge_gaps=int(meta.get("knowledge_gaps") or 0),
                summary=(
                    f"Research incomplete: artifacts={len(report.missing)} missing, "
                    f"quality={quality.details.get('false_completion_count', 0)} false-completion"
                ),
                recommended_next_phase="RESEARCH",
                metadata={
                    "missing": report.missing[:10],
                    "quality_missing": quality.missing[:10],
                    "execution_mode": "IN_PROCESS_CLOUD",
                    "authoritative_research": False,
                },
                idempotency_key=f"{task.batch_id}:RESEARCH:{task.run_id}",
            )

        return PhaseResult(
            run_id=task.run_id,
            batch_id=task.batch_id,
            phase="RESEARCH",
            status="SUCCESS",
            started_at=started,
            completed_at=self._now(),
            services_total=int(meta.get("services_in_scope") or len(service_ids)),
            services_processed=int(meta.get("services_researched") or 0),
            claims_total=int(meta.get("claims_total") or 0),
            knowledge_gaps=int(meta.get("knowledge_gaps") or 0),
            conflicting=int(meta.get("conflicts") or 0),
            summary=f"Research complete with service-specific quality: {meta.get('claims_total', 0)} claims",
            recommended_next_phase="VERIFICATION",
            metadata={"execution_mode": "IN_PROCESS_CLOUD", "authoritative_research": True},
            idempotency_key=f"{task.batch_id}:RESEARCH:complete",
        )

    def _execute_verification(self, task: CloudTaskSpec, batch: dict[str, Any], started: str) -> PhaseResult:
        slug = batch_slug(batch)
        prefix = self._batch_script_prefix(slug)
        script = f"verify_{prefix}_claims.py"
        if (self.repo_root / "scripts" / script).exists():
            return self._execute_via_legacy_or_partial(task, batch, started)

        result = self.verification_builder.build_batch_verification(batch)
        if not result.get("complete"):
            return PhaseResult(
                run_id=task.run_id,
                batch_id=task.batch_id,
                phase="VERIFICATION",
                status="FAILED",
                started_at=started,
                completed_at=self._now(),
                summary=result.get("error", "Verification builder failed"),
                recommended_next_phase="VERIFICATION",
                metadata={"execution_mode": "IN_PROCESS_CLOUD"},
                idempotency_key=f"{task.batch_id}:VERIFICATION:{task.run_id}",
            )

        summary = result.get("summary") or {}
        gaps = int(summary.get("knowledge_gaps") or 0)
        return PhaseResult(
            run_id=task.run_id,
            batch_id=task.batch_id,
            phase="VERIFICATION",
            status="SUCCESS",
            started_at=started,
            completed_at=self._now(),
            claims_total=int(summary.get("claims_total") or 0),
            verified=int(summary.get("verified") or 0),
            partial=int(summary.get("partially_verified") or 0),
            unverified=int(summary.get("unverified") or 0),
            knowledge_gaps=gaps,
            summary=f"Verification complete via generic builder: {summary.get('verified', 0)} verified, {gaps} gaps",
            recommended_next_phase="GAP_CLOSURE" if gaps > 0 else "PUBLICATION",
            metadata={"execution_mode": "IN_PROCESS_CLOUD", "builder": "generic_verification_builder"},
            idempotency_key=f"{task.batch_id}:VERIFICATION:complete",
        )

    def _execute_gap_closure(self, task: CloudTaskSpec, batch: dict[str, Any], started: str) -> PhaseResult:
        slug = batch_slug(batch)
        prefix = self._batch_script_prefix(slug)
        script = f"generate_{prefix}_gap_closure.py"
        if (self.repo_root / "scripts" / script).exists():
            return self._execute_via_legacy_or_partial(task, batch, started)

        result = self.gap_closure_builder.build_gap_closure(batch)
        summary = result.get("summary") or {}
        return PhaseResult(
            run_id=task.run_id,
            batch_id=task.batch_id,
            phase="GAP_CLOSURE",
            status="SUCCESS",
            started_at=started,
            completed_at=self._now(),
            knowledge_gaps=int(summary.get("deferred") or 0),
            summary=f"Gap closure deferred {summary.get('deferred', 0)} items — no invented data",
            recommended_next_phase="PUBLICATION",
            metadata={"execution_mode": "IN_PROCESS_CLOUD", "builder": "generic_gap_closure_builder"},
            idempotency_key=f"{task.batch_id}:GAP_CLOSURE:complete",
        )

    def _execute_via_legacy_or_partial(
        self, task: CloudTaskSpec, batch: dict[str, Any], started: str
    ) -> PhaseResult:
        """Phases with legacy scripts run via subprocess; E2E falls back to generic evaluator."""
        slug = batch_slug(batch)
        prefix = self._batch_script_prefix(slug)
        script_map = {
            "VERIFICATION": f"verify_{prefix}_claims.py",
            "GAP_CLOSURE": f"generate_{prefix}_gap_closure.py",
            "PUBLICATION": None,
            "E2E": f"evaluate_{prefix}_e2e.py",
        }
        script = script_map.get(task.phase)

        if task.phase == "E2E" and script and not (self.repo_root / "scripts" / script).exists():
            cmd = [
                sys.executable,
                str(self.repo_root / "scripts" / "evaluate_generic_batch_e2e.py"),
                "--batch",
                slug,
                *["--service-ids", *list(batch.get("service_ids") or [])],
            ]
            proc = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=900,
            )
            completion = phase_artifacts_complete(self.repo_root, batch, task.phase)
            summary_path = self.repo_root / "data" / "evaluation" / slug / "summary.json"
            metrics: dict[str, Any] = {}
            if summary_path.exists():
                metrics = json.loads(summary_path.read_text(encoding="utf-8"))
            if proc.returncode == 0 and completion.complete:
                return PhaseResult(
                    run_id=task.run_id,
                    batch_id=task.batch_id,
                    phase="E2E",
                    status="SUCCESS",
                    started_at=started,
                    completed_at=self._now(),
                    e2e_total=int(metrics.get("total") or 0),
                    e2e_passed=int(metrics.get("passed") or 0),
                    e2e_failed=int(metrics.get("failed") or 0),
                    hallucinations=int(metrics.get("hallucinations") or 0),
                    citation_failures=int(metrics.get("citation_failures") or 0),
                    summary=f"E2E complete via generic evaluator: {metrics.get('passed', 0)}/{metrics.get('total', 0)}",
                    recommended_next_phase="REGRESSION",
                    metadata={"execution_mode": "IN_PROCESS_CLOUD", "script": "evaluate_generic_batch_e2e.py"},
                    idempotency_key=f"{task.batch_id}:E2E:complete",
                )

        if script and (self.repo_root / "scripts" / script).exists():
            proc = subprocess.run(
                [sys.executable, str(self.repo_root / "scripts" / script)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=900,
            )
            completion = phase_artifacts_complete(self.repo_root, batch, task.phase)
            if proc.returncode == 0 and completion.complete:
                nxt = {
                    "VERIFICATION": "GAP_CLOSURE",
                    "GAP_CLOSURE": "PUBLICATION",
                    "PUBLICATION": "E2E",
                    "E2E": "REGRESSION",
                }.get(task.phase, "")
                return PhaseResult(
                    run_id=task.run_id,
                    batch_id=task.batch_id,
                    phase=task.phase,
                    status="SUCCESS",
                    started_at=started,
                    completed_at=self._now(),
                    summary=f"{task.phase} complete via legacy script",
                    recommended_next_phase=nxt,
                    metadata={"execution_mode": "IN_PROCESS_CLOUD", "script": script},
                    idempotency_key=f"{task.batch_id}:{task.phase}:complete",
                )

        return PhaseResult(
            run_id=task.run_id,
            batch_id=task.batch_id,
            phase=task.phase,
            status="PARTIAL",
            started_at=started,
            completed_at=self._now(),
            summary=f"{task.phase} requires dedicated cloud agent task — script not yet generated",
            recommended_next_phase=task.phase,
            metadata={
                "execution_mode": "IN_PROCESS_CLOUD",
                "needs_cloud_agent": True,
                "script": script,
            },
            idempotency_key=f"{task.batch_id}:{task.phase}:{task.run_id}",
        )
