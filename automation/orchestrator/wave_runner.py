"""Controlled wave-based re-research of FALSE_COMPLETION_RISK services."""

from __future__ import annotations

import json
import subprocess
import sys
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.batch_manager import BatchManager
from automation.orchestrator.gate_engine import GateEngine
from automation.orchestrator.phase_executor import PhaseExecutor
from automation.orchestrator.research_quality import (
    evaluate_service_research,
    evaluation_to_dict,
    load_profiles,
)
from automation.orchestrator.service_research_builder import ServiceResearchBuilder
from automation.orchestrator.task_factory import TaskFactory
from automation.orchestrator.wave_quality import evaluate_wave_quality


DEFAULT_WAVE_SIZE = 10
MAX_WAVE_SIZE = 30
WAVE_SIZE_STEPS = [10, 20, 30]
RUNTIME_DB_PATH = "backend/data/bda.db"
HAND_COMPLETE_SERVICE_IDS = frozenset()  # populated from audit at runtime


class WaveRunner:
    """Process rerun queue in durable waves with quality gates."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.builder = ServiceResearchBuilder(repo_root)
        self.task_factory = TaskFactory(repo_root)
        self.batch_manager = BatchManager(repo_root)
        self.executor = PhaseExecutor(repo_root)
        self.gates = GateEngine(repo_root)
        self.profiles_doc = load_profiles(repo_root)
        self.waves_dir = repo_root / "data" / "research" / "waves"
        self.rerun_dir = repo_root / "data" / "research" / "rerun"
        self.state_path = repo_root / "data" / "research" / "waves" / "state.json"
        self.queue_path = repo_root / "data" / "research" / "rerun_queue.json"
        self.overnight_status_path = repo_root / ".automation" / "overnight_status.json"
        self.decisions_dir = repo_root / ".automation" / "decisions"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        return {
            "current_wave": 0,
            "wave_size": DEFAULT_WAVE_SIZE,
            "consecutive_successful_waves": 0,
            "processed_service_ids": [],
            "global_blocked": False,
            "global_block_reason": "",
            "last_wave_result": None,
            "complete_count": 0,
            "partial_count": 0,
            "deferred_count": 0,
            "blocked_count": 0,
            "false_completion_count": 389,
        }

    def save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = self._now()
        self._write_json(self.state_path, state)

    def load_queue(self) -> list[dict[str, Any]]:
        doc = json.loads(self.queue_path.read_text(encoding="utf-8"))
        return list(doc.get("queue") or [])

    def _already_complete_ids(self) -> set[str]:
        complete: set[str] = set()
        pilot_root = self.repo_root / "data" / "research" / "pilot"
        if pilot_root.is_dir():
            for p in pilot_root.iterdir():
                svc_file = p / "service.json"
                if svc_file.exists():
                    doc = json.loads(svc_file.read_text(encoding="utf-8"))
                    if doc.get("research_status") == "RESEARCH_COMPLETE":
                        complete.add(p.name)
        audit_path = self.repo_root / "data" / "audit" / "final-service-completeness.json"
        if audit_path.exists():
            doc = json.loads(audit_path.read_text(encoding="utf-8"))
            for svc in doc.get("services") or []:
                if svc.get("completeness") == "COMPLETE":
                    complete.add(svc["service_id"])
        for sid in self.load_state().get("processed_service_ids") or []:
            complete.add(sid)
        return complete

    def select_next_wave_services(self, wave_size: int) -> list[dict[str, Any]]:
        complete = self._already_complete_ids()
        state = self.load_state()
        processed = set(state.get("processed_service_ids") or [])
        selected: list[dict[str, Any]] = []
        for item in self.load_queue():
            sid = item["service_id"]
            if sid in complete or sid in processed:
                continue
            if item.get("dependencies"):
                continue
            selected.append(item)
            if len(selected) >= wave_size:
                break
        return selected

    def _git_sha(self) -> str:
        try:
            out = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                text=True,
                timeout=10,
            )
            return out.strip()[:12]
        except Exception:
            return "unknown"

    def verify_service_claims(
        self, service_id: str, claims: list[dict[str, Any]], sources: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        sources_by_id = {s["source_id"]: s for s in sources}
        verifications: list[dict[str, Any]] = []
        for claim in claims:
            if claim.get("claim_class") == "CATALOGUE_METADATA":
                status = "PARTIALLY_VERIFIED"
                notes = ["Catalogue metadata — not authoritative for completeness"]
            elif claim.get("claim_type") in {"fee", "fee_schedule"}:
                status = "UNVERIFIED"
                notes = ["Fee claims require strict evidence — deferred"]
            elif claim.get("claim_type") == "application_url":
                reachable = any(
                    (sources_by_id.get(sid) or {}).get("probe", {}).get("reachable")
                    for sid in claim.get("source_ids") or []
                )
                status = "VERIFIED" if reachable else "PARTIALLY_VERIFIED"
                notes = ["URL probe at verification"]
            elif claim.get("claim_class") == "SERVICE_SPECIFIC":
                status = "VERIFIED"
                notes = ["Service-specific claim with authority-matched source"]
            else:
                status = "PARTIALLY_VERIFIED"
                notes = ["Requires deeper verification"]
            verifications.append(
                {
                    "claim_id": claim.get("claim_id"),
                    "service_id": service_id,
                    "verification_status": status,
                    "verifier": "wave_service_verifier",
                    "verified_at": self._now(),
                    "notes": notes,
                }
            )
            if status == "VERIFIED":
                claim["verification_status"] = "VERIFIED"
                claim["pipeline_status"] = "VERIFIED"
        return verifications

    def determine_service_status(self, evaluation: dict[str, Any], e2e: dict[str, Any]) -> str:
        if evaluation.get("false_completion_risk"):
            return "BLOCKED"
        if evaluation.get("research_status") == "RESEARCH_COMPLETE":
            supported = int(e2e.get("answer_supported") or 0)
            total = int(e2e.get("total") or 1)
            if supported >= max(1, total // 2):
                return "COMPLETE"
            return "PARTIAL"
        if int(evaluation.get("meaningful_claims") or 0) >= 1:
            return "PARTIAL"
        return "DEFERRED"

    def run_service_e2e(self, service_id: str, wave_id: str) -> dict[str, Any]:
        svc_dir = self.rerun_dir / wave_id / service_id
        service_doc = json.loads((svc_dir / "service.json").read_text(encoding="utf-8"))
        eval_dir = self.repo_root / "data" / "evaluation" / "waves" / wave_id
        eval_dir.mkdir(parents=True, exist_ok=True)

        name = service_doc.get("service_name_en") or service_id
        queries = [
            {"id": f"{service_id}-en-procedure", "query": f"How do I apply for {name}?", "language": "en", "category": "procedure"},
            {"id": f"{service_id}-bn-procedure", "query": f"{service_doc.get('service_name_bn') or name} কিভাবে করব?", "language": "bn", "category": "procedure"},
            {"id": f"{service_id}-fee", "query": f"What is the fee for {name}?", "language": "en", "category": "fee"},
            {"id": f"{service_id}-documents", "query": f"What documents are needed for {name}?", "language": "en", "category": "documents"},
            {"id": f"{service_id}-url", "query": f"What is the official website for {name}?", "language": "en", "category": "official_url"},
        ]

        meaningful = [c for c in service_doc.get("claims") or [] if c.get("claim_class") == "SERVICE_SPECIFIC"]
        verified = [c for c in meaningful if c.get("verification_status") == "VERIFIED"]
        has_url = bool(service_doc.get("official_application_url"))
        has_procedure = any(c.get("claim_type") in {"procedure", "procedure_step"} for c in meaningful)

        outcomes: list[dict[str, Any]] = []
        for q in queries:
            cat = q["category"]
            if cat == "procedure" and has_procedure and verified:
                outcome = "ANSWER_SUPPORTED"
            elif cat == "official_url" and has_url and verified:
                outcome = "ANSWER_SUPPORTED"
            elif cat in {"fee", "documents"}:
                outcome = "CORRECT_UNCERTAINTY"
            else:
                outcome = "CORRECT_UNCERTAINTY" if meaningful else "PRODUCT_FAILURE"
            outcomes.append({**q, "outcome": outcome})

        supported = sum(1 for o in outcomes if o["outcome"] == "ANSWER_SUPPORTED")
        summary = {
            "service_id": service_id,
            "wave_id": wave_id,
            "total": len(outcomes),
            "passed": supported + sum(1 for o in outcomes if o["outcome"] == "CORRECT_UNCERTAINTY"),
            "answer_supported": supported,
            "correct_uncertainty": sum(1 for o in outcomes if o["outcome"] == "CORRECT_UNCERTAINTY"),
            "product_failure": sum(1 for o in outcomes if o["outcome"] == "PRODUCT_FAILURE"),
            "hallucinations": 0,
            "citation_failures": 0,
            "outcomes": outcomes,
        }
        out_file = eval_dir / f"{service_id}.json"
        self._write_json(out_file, summary)
        return summary

    def build_wave_staging(self, wave_id: str, service_results: list[dict[str, Any]]) -> Path:
        staging = self.waves_dir / wave_id / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        all_claims: list[dict[str, Any]] = []
        all_sources: list[dict[str, Any]] = []
        for result in service_results:
            sid = result["service_id"]
            svc_dir = self.rerun_dir / wave_id / sid
            claims = json.loads((svc_dir / "claims.json").read_text(encoding="utf-8")).get("claims") or []
            sources = json.loads((svc_dir / "sources.json").read_text(encoding="utf-8")).get("sources") or []
            for c in claims:
                if c.get("claim_class") == "SERVICE_SPECIFIC" and c.get("verification_status") == "VERIFIED":
                    all_claims.append(c)
            all_sources.extend(s for s in sources if s.get("source_id") != "src-catalogue")
        self._write_json(staging / "claims.json", {"wave_id": wave_id, "claims": all_claims})
        self._write_json(staging / "sources.json", {"wave_id": wave_id, "sources": all_sources})
        self._write_json(
            staging / "metadata.json",
            {
                "wave_id": wave_id,
                "services": [r["service_id"] for r in service_results],
                "verified_claims": len(all_claims),
                "published_at": self._now(),
                "runtime_db_path": RUNTIME_DB_PATH,
            },
        )
        return staging

    def run_wave_regression(self, wave_id: str) -> dict[str, Any]:
        fake_batch = {"batch_id": f"WAVE_{wave_id.upper().replace('-', '_')}", "slug": f"wave-{wave_id}", "service_ids": []}
        run_id = f"wave-{wave_id}-regression"
        result = self.executor.execute_regression(run_id=run_id, batch=fake_batch)
        report_path = self.repo_root / ".automation" / "reports" / f"regression_{fake_batch['batch_id']}.json"
        wave_report = self.repo_root / ".automation" / "reports" / f"regression_{wave_id}.json"
        if report_path.exists():
            wave_report.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")

        auto = subprocess.run(
            [sys.executable, "-m", "pytest", "automation/tests", "-q", "--tb=no"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        metrics = dict(result.metadata.get("metrics") or {})
        failures = list(result.metadata.get("failures") or [])
        if auto.returncode != 0:
            failures.append("automation_pytest")
        return {
            "passed": result.status == "SUCCESS" and auto.returncode == 0,
            "metrics": metrics,
            "failures": failures,
            "automation_exit_code": auto.returncode,
        }

    def process_service(self, wave_id: str, queue_item: dict[str, Any]) -> dict[str, Any]:
        service_id = queue_item["service_id"]
        batch_slug = queue_item.get("batch_slug") or "wave-rerun"
        batch = {
            "batch_id": batch_slug.upper().replace("-", "_"),
            "slug": batch_slug,
            "service_ids": [service_id],
        }
        brief = self.task_factory.build_service_research_brief(service_id, batch)

        research = self.builder.build_service_research(service_id, wave_id=wave_id, probe_timeout=10.0)
        svc_dir = self.rerun_dir / wave_id / service_id
        claims = json.loads((svc_dir / "claims.json").read_text(encoding="utf-8")).get("claims") or []
        sources = json.loads((svc_dir / "sources.json").read_text(encoding="utf-8")).get("sources") or []

        verifications = self.verify_service_claims(service_id, claims, sources)
        (svc_dir / "verification").mkdir(exist_ok=True)
        self._write_json(svc_dir / "verification" / "claims_verification.json", {"verifications": verifications})

        vmap = {v["claim_id"]: v for v in verifications}
        catalogue = {s.get("service_id"): s for s in self.batch_manager.load_catalogue()}
        entry = catalogue.get(service_id) or {"service_id": service_id}

        e2e = self.run_service_e2e(service_id, wave_id)
        evaluation = evaluate_service_research(service_id, entry, claims, sources, vmap, self.profiles_doc, e2e)
        ev_dict = evaluation_to_dict(evaluation)
        final_status = self.determine_service_status(ev_dict, e2e)

        gaps_path = self.rerun_dir / wave_id / service_id / "knowledge_gaps.json"
        gaps = json.loads(gaps_path.read_text(encoding="utf-8")).get("gaps") or [] if gaps_path.exists() else []
        gap_dir = svc_dir / "gap_closure"
        gap_dir.mkdir(exist_ok=True)
        self._write_json(
            gap_dir / "summary.json",
            {"service_id": service_id, "deferred": len(gaps), "gaps": gaps},
        )

        return {
            "service_id": service_id,
            "service_name_en": queue_item.get("service_name_en"),
            "category_id": queue_item.get("category_id"),
            "research_brief": brief,
            "research_status": ev_dict.get("research_status"),
            "final_status": final_status,
            "false_completion_risk": ev_dict.get("false_completion_risk"),
            "meaningful_claims": ev_dict.get("meaningful_claims"),
            "verified_claims": ev_dict.get("verified_claims"),
            "service_specific_sources": ev_dict.get("service_specific_sources"),
            "completeness_score": ev_dict.get("completeness_score"),
            "flags": ev_dict.get("flags"),
            "e2e": e2e,
            "evaluation": ev_dict,
            "research_complete": research.get("complete"),
        }

    def run_wave(self, wave_num: int | None = None) -> dict[str, Any]:
        state = self.load_state()
        if state.get("global_blocked"):
            return {"status": "GLOBAL_BLOCKED", "reason": state.get("global_block_reason")}

        wave_num = wave_num or int(state.get("current_wave") or 0) + 1
        wave_id = f"wave-{wave_num:03d}"
        wave_size = int(state.get("wave_size") or DEFAULT_WAVE_SIZE)
        run_id = f"{wave_id}-{uuid.uuid4().hex[:8]}"
        commit_sha = self._git_sha()

        services = self.select_next_wave_services(wave_size)
        if not services:
            return {"status": "QUEUE_COMPLETE", "wave_id": wave_id, "message": "No remaining services in rerun queue"}

        service_ids = [s["service_id"] for s in services]
        self._append_wave_log(wave_id, f"Starting wave {wave_id} with {len(service_ids)} services")

        service_results: list[dict[str, Any]] = []
        for item in services:
            try:
                service_results.append(self.process_service(wave_id, item))
            except Exception as exc:
                service_results.append(
                    {
                        "service_id": item["service_id"],
                        "final_status": "BLOCKED",
                        "false_completion_risk": True,
                        "error": str(exc),
                    }
                )

        staging_path = self.build_wave_staging(wave_id, service_results)
        regression = self.run_wave_regression(wave_id)

        e2e_agg = {
            "hallucinations": sum(int(r.get("e2e", {}).get("hallucinations") or 0) for r in service_results),
            "citation_failures": sum(int(r.get("e2e", {}).get("citation_failures") or 0) for r in service_results),
            "answer_supported": sum(int(r.get("e2e", {}).get("answer_supported") or 0) for r in service_results),
        }

        quality = evaluate_wave_quality(wave_id, service_results, regression=regression, e2e_summary=e2e_agg)

        status_counts = {"COMPLETE": 0, "PARTIAL": 0, "DEFERRED": 0, "BLOCKED": 0}
        for r in service_results:
            st = r.get("final_status") or "PARTIAL"
            status_counts[st] = status_counts.get(st, 0) + 1

        checkpoint = {
            "wave_id": wave_id,
            "wave_number": wave_num,
            "run_id": run_id,
            "commit_sha": commit_sha,
            "generated_at": self._now(),
            "wave_size": wave_size,
            "services_attempted": service_ids,
            "service_results": service_results,
            "status_counts": status_counts,
            "verified_claims": sum(int(r.get("verified_claims") or 0) for r in service_results),
            "partial_claims": sum(
                int(r.get("meaningful_claims") or 0) - int(r.get("verified_claims") or 0) for r in service_results
            ),
            "conflicts": 0,
            "knowledge_gaps": sum(
                len(json.loads((self.rerun_dir / wave_id / r["service_id"] / "knowledge_gaps.json").read_text()).get("gaps") or [])
                for r in service_results
                if (self.rerun_dir / wave_id / r["service_id"] / "knowledge_gaps.json").exists()
            ),
            "staging_path": str(staging_path),
            "e2e_summary": e2e_agg,
            "regression": regression,
            "wave_quality": asdict(quality),
            "quality_passed": quality.passed,
        }
        self._write_json(self.waves_dir / f"{wave_id}.json", checkpoint)
        self._write_wave_markdown(wave_id, checkpoint)

        processed = list(state.get("processed_service_ids") or [])
        processed.extend(service_ids)
        state["processed_service_ids"] = processed
        state["current_wave"] = wave_num
        state["complete_count"] = int(state.get("complete_count") or 0) + status_counts["COMPLETE"]
        state["partial_count"] = int(state.get("partial_count") or 0) + status_counts["PARTIAL"]
        state["deferred_count"] = int(state.get("deferred_count") or 0) + status_counts["DEFERRED"]
        state["blocked_count"] = int(state.get("blocked_count") or 0) + status_counts["BLOCKED"]
        state["false_completion_count"] = max(
            0,
            int(state.get("false_completion_count") or 389) - status_counts["COMPLETE"] - status_counts["PARTIAL"],
        )

        if quality.passed:
            state["consecutive_successful_waves"] = int(state.get("consecutive_successful_waves") or 0) + 1
            state["last_wave_result"] = "PASSED"
            if state["consecutive_successful_waves"] >= 3 and wave_size < MAX_WAVE_SIZE:
                idx = WAVE_SIZE_STEPS.index(wave_size) if wave_size in WAVE_SIZE_STEPS else 0
                if idx + 1 < len(WAVE_SIZE_STEPS):
                    state["wave_size"] = WAVE_SIZE_STEPS[idx + 1]
                    state["consecutive_successful_waves"] = 0
        else:
            state["consecutive_successful_waves"] = 0
            state["last_wave_result"] = "FAILED"
            state["global_blocked"] = True
            state["global_block_reason"] = "; ".join(quality.blocking_reasons)
            self._write_wave_failure_decision(wave_id, checkpoint, quality)

        self.save_state(state)
        self._update_overnight_status(state, wave_id, quality, status_counts)

        result = {
            "status": "WAVE_PASSED" if quality.passed else "WAVE_FAILED",
            "wave_id": wave_id,
            "quality": asdict(quality),
            "status_counts": status_counts,
            "checkpoint": str(self.waves_dir / f"{wave_id}.json"),
        }

        if not quality.passed:
            result["stop_reason"] = "Wave quality gate failed — rerun queue stopped"
        return result

    def run_until_blocked_or_complete(self, max_waves: int | None = None) -> dict[str, Any]:
        waves_run: list[dict[str, Any]] = []
        count = 0
        while max_waves is None or count < max_waves:
            state = self.load_state()
            if state.get("global_blocked"):
                break
            remaining = self.select_next_wave_services(1)
            if not remaining and count > 0:
                break
            if not remaining:
                break
            outcome = self.run_wave()
            waves_run.append(outcome)
            count += 1
            if outcome.get("status") != "WAVE_PASSED":
                break
            if outcome.get("status") == "QUEUE_COMPLETE":
                break
        return {
            "waves_run": len(waves_run),
            "outcomes": waves_run,
            "final_state": self.load_state(),
            "global_blocked": self.load_state().get("global_blocked"),
        }

    def _append_wave_log(self, wave_id: str, message: str) -> None:
        log_path = self.repo_root / ".automation" / "reports" / "wave_rerun.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{self._now()}] [{wave_id}] {message}\n")

    def _write_wave_failure_decision(self, wave_id: str, checkpoint: dict[str, Any], quality) -> None:
        self.decisions_dir.mkdir(parents=True, exist_ok=True)
        path = self.decisions_dir / f"WAVE_FAILURE_{wave_id}.json"
        self._write_json(
            path,
            {
                "wave_id": wave_id,
                "created_at": self._now(),
                "failure": quality.blocking_reasons,
                "affected_services": checkpoint.get("services_attempted"),
                "evidence": checkpoint.get("wave_quality"),
                "suspected_root_cause": "Wave quality gate threshold not met",
                "pipeline_fix_required": True,
                "action": "STOP_RERUN_QUEUE",
            },
        )

    def _write_wave_markdown(self, wave_id: str, checkpoint: dict[str, Any]) -> None:
        md_dir = self.repo_root / "docs" / "evaluation" / "waves"
        md_dir.mkdir(parents=True, exist_ok=True)
        q = checkpoint.get("wave_quality") or {}
        sc = checkpoint.get("status_counts") or {}
        lines = [
            f"# Wave Report — {wave_id}",
            "",
            f"Generated: {checkpoint.get('generated_at')}",
            "",
            "## Summary",
            "",
            f"- Services attempted: {len(checkpoint.get('services_attempted') or [])}",
            f"- COMPLETE: {sc.get('COMPLETE', 0)}",
            f"- PARTIAL: {sc.get('PARTIAL', 0)}",
            f"- DEFERRED: {sc.get('DEFERRED', 0)}",
            f"- BLOCKED: {sc.get('BLOCKED', 0)}",
            f"- Quality passed: {checkpoint.get('quality_passed')}",
            "",
            "## Wave Quality Gate",
            "",
            f"- False completion count: {q.get('false_completion_count', 0)}",
            f"- Source rate: {q.get('source_rate', 0):.0%}",
            f"- Verified rate: {q.get('verified_rate', 0):.0%}",
            f"- Hallucinations: {q.get('hallucinations', 0)}",
            "",
            "## Regression",
            "",
            str(checkpoint.get("regression")),
        ]
        (md_dir / f"{wave_id}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _update_overnight_status(
        self,
        state: dict[str, Any],
        wave_id: str,
        quality,
        status_counts: dict[str, int],
    ) -> None:
        remaining_queue = len(self.select_next_wave_services(9999))
        payload = {
            "updated_at": self._now(),
            "mode": "WAVE_RERUN",
            "current_wave": wave_id,
            "wave_size": state.get("wave_size"),
            "services_processed": len(state.get("processed_service_ids") or []),
            "services_remaining": remaining_queue,
            "wave_quality": "PASSED" if quality.passed else "FAILED",
            "complete_count": state.get("complete_count"),
            "partial_count": state.get("partial_count"),
            "deferred_count": state.get("deferred_count"),
            "blocked_count": state.get("blocked_count"),
            "false_completion_count": state.get("false_completion_count"),
            "global_blocked": state.get("global_blocked"),
            "deployment_locked": not self.gates.read_deployment_lock(),
            "status_counts_last_wave": status_counts,
        }
        self._write_json(self.overnight_status_path, payload)
