"""Standard deep-research pipeline: research → verify → publish → runtime validate → E2E."""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestrator.claim_density import score_claim_density
from automation.orchestrator.deep_research_builder import DeepResearchBuilder
from automation.orchestrator.deep_research_staging import BATCH_SLUG, DeepResearchStagingBuilder
from automation.orchestrator.phase_executor import PhaseExecutor
from automation.orchestrator.research_quality import evaluate_service_research, evaluation_to_dict, load_profiles, resolve_profile_key
from automation.orchestrator.runtime_validator import RuntimeValidator

PILOT_OUTPUT = "deep-research-pilot-20"

STEP31_EXCLUDED = frozenset(
    {
        "nid-new-voter-registration",
        "education-ssc-certificate",
        "tax-income-return-file",
        "business-company-incorporation",
        "land-mutation-apply",
        "land-khatian-certified-copy",
        "education-foreign-equivalency",
        "education-duplicate-certificate",
        "snp-old-age-allowance",
        "disability-dis-registration",
        "health-bmdc-full-registration",
        "judiciary-supreme-court-e-filing",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DeepResearchServiceResult:
    service_id: str
    output_dir: str
    verified_claims: int
    document_coverage: dict[str, int]
    conditional_coverage: int
    fee_coverage: bool
    supported_answer_coverage: float
    runtime_publication: dict[str, Any]
    retrieval_accuracy: float
    citation_correct: bool
    issues: list[str] = field(default_factory=list)


@dataclass
class WaveGateResult:
    wave_id: str
    passed: bool
    services_processed: int
    avg_supported_coverage: float
    avg_retrieval_accuracy: float
    citation_accuracy: float
    failures: list[str] = field(default_factory=list)


class DeepResearchPipeline:
    """Canonical pipeline for PARTIAL services — not shallow wave rerun."""

    SUPPORTED_COVERAGE_TARGET = 0.75
    RETRIEVAL_ACCURACY_TARGET = 0.95
    CITATION_ACCURACY_TARGET = 1.0

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_root = repo_root / "data" / "research" / PILOT_OUTPUT
        self.eval_root = repo_root / "data" / "evaluation" / PILOT_OUTPUT
        self.builder = DeepResearchBuilder(repo_root, output_subdir=PILOT_OUTPUT)
        self.staging_builder = DeepResearchStagingBuilder(repo_root)
        self.runtime_validator = RuntimeValidator(repo_root)
        self.profiles_doc = load_profiles(repo_root)
        self.catalogue = self._load_catalogue()

    def _load_catalogue(self) -> dict[str, dict[str, Any]]:
        path = self.repo_root / "data" / "service_catalogue" / "services.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        services = doc.get("services") if isinstance(doc, dict) else doc
        return {s["service_id"]: s for s in services if isinstance(s, dict) and s.get("service_id")}

    def _document_coverage(self, claims: list[dict[str, Any]]) -> dict[str, int]:
        counts = {"MUST_NEED": 0, "CONDITIONAL": 0, "RECOMMENDED": 0, "NOT_APPLICABLE": 0}
        for claim in claims:
            if claim.get("claim_type") not in {"document", "document_requirement", "conditional_document"}:
                continue
            cond = claim.get("condition") or {}
            rc = cond.get("requirement_class") or "MUST_NEED"
            if rc not in counts:
                rc = "MUST_NEED"
            counts[rc] += 1
        return counts

    def research_service(self, service_id: str) -> DeepResearchServiceResult:
        deep = self.builder.build_deep_research(service_id)
        verification = self.builder.verify_deep_claims(service_id)
        e2e = self.builder.run_deep_e2e(service_id, verification["verification_map"])

        out_dir = Path(deep["output_dir"])
        claims = json.loads((out_dir / "claims.json").read_text(encoding="utf-8")).get("claims") or []
        entry = self.catalogue.get(service_id) or {"service_id": service_id}
        profile_key = resolve_profile_key(entry, self.profiles_doc)
        evaluation = evaluate_service_research(
            service_id,
            entry,
            claims,
            json.loads((out_dir / "sources.json").read_text(encoding="utf-8")).get("sources") or [],
            verification["verification_map"],
            self.profiles_doc,
            e2e,
        )
        ev = evaluation_to_dict(evaluation)
        density = score_claim_density(service_id, profile_key, claims, ev.get("dimension_coverage") or {})

        verified = sum(1 for c in claims if c.get("verification_status") == "VERIFIED")
        doc_cov = self._document_coverage(claims)
        conditional = doc_cov.get("CONDITIONAL", 0) + sum(
            1 for c in claims if (c.get("condition") or {}).get("if")
        )
        fee_cov = any(c.get("claim_type") in {"fee", "fee_schedule"} for c in claims)

        return DeepResearchServiceResult(
            service_id=service_id,
            output_dir=str(out_dir),
            verified_claims=verified,
            document_coverage=doc_cov,
            conditional_coverage=conditional,
            fee_coverage=fee_cov,
            supported_answer_coverage=float(e2e.get("supported_answer_coverage") or 0),
            runtime_publication={},
            retrieval_accuracy=0.0,
            citation_correct=True,
            issues=[],
        )

    def build_staging(self, service_ids: list[str]) -> Path:
        dirs = [self.output_root / sid for sid in service_ids if (self.output_root / sid).exists()]
        return self.staging_builder.build_from_service_dirs(dirs, self.catalogue)

    def publish_to_runtime(self, *, dry_run: bool = False) -> dict[str, Any]:
        cmd = [
            sys.executable,
            str(self.repo_root / "scripts" / "publish_verified_knowledge.py"),
            "--batch",
            BATCH_SLUG,
            "--sync-claims",
            "--publish",
        ]
        if dry_run:
            cmd.append("--dry-run")
        else:
            cmd.append("--commit")
        proc = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True, timeout=300)
        payload: dict[str, Any] = {"returncode": proc.returncode, "stdout": proc.stdout[-4000:] if proc.stdout else ""}
        if proc.returncode != 0:
            payload["stderr"] = proc.stderr[-2000:] if proc.stderr else ""
        try:
            payload["report"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            pass
        return payload

    async def validate_runtime(self, service_ids: list[str]) -> dict[str, Any]:
        names = {
            sid: (self.catalogue.get(sid) or {}).get("service_name_en") or sid for sid in service_ids
        }
        report = await self.runtime_validator.validate_batch(
            service_ids, batch_slug=BATCH_SLUG, service_names=names
        )
        audit_path = self.runtime_validator.write_audit(report)
        return {"audit_path": str(audit_path), **asdict(report)}

    def run_regression(self) -> dict[str, Any]:
        executor = PhaseExecutor(self.repo_root)
        batch = {"batch_id": "DEEP_RESEARCH_PILOT_20", "slug": PILOT_OUTPUT, "service_ids": []}
        result = executor.execute_regression(run_id="deep-research-pilot-20-regression", batch=batch)
        auto = subprocess.run(
            [sys.executable, "-m", "pytest", "automation/tests", "backend/tests", "-q", "--tb=no"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return {
            "regression_passed": result.status == "SUCCESS" and auto.returncode == 0,
            "regression_status": result.status,
            "automation_backend_tests": auto.returncode == 0,
            "test_output_tail": auto.stdout.splitlines()[-5:] if auto.stdout else [],
        }

    def evaluate_wave_gate(self, results: list[DeepResearchServiceResult], wave_id: str) -> WaveGateResult:
        failures: list[str] = []
        if not results:
            return WaveGateResult(wave_id, False, 0, 0.0, 0.0, 0.0, ["no services processed"])

        avg_supported = sum(r.supported_answer_coverage for r in results) / len(results)
        avg_retrieval = sum(r.retrieval_accuracy for r in results) / len(results)
        citation_ok = all(r.citation_correct for r in results)
        citation_accuracy = 1.0 if citation_ok else 0.0

        if avg_supported < self.SUPPORTED_COVERAGE_TARGET:
            failures.append(f"supported_answer_coverage {avg_supported:.2%} < {self.SUPPORTED_COVERAGE_TARGET:.0%}")
        if avg_retrieval < self.RETRIEVAL_ACCURACY_TARGET:
            failures.append(f"retrieval_accuracy {avg_retrieval:.2%} < {self.RETRIEVAL_ACCURACY_TARGET:.0%}")
        if citation_accuracy < self.CITATION_ACCURACY_TARGET:
            failures.append("citation correctness below 100%")

        for r in results:
            if r.issues:
                failures.extend(f"{r.service_id}: {i}" for i in r.issues)

        return WaveGateResult(
            wave_id=wave_id,
            passed=len(failures) == 0,
            services_processed=len(results),
            avg_supported_coverage=round(avg_supported, 4),
            avg_retrieval_accuracy=round(avg_retrieval, 4),
            citation_accuracy=citation_accuracy,
            failures=failures,
        )

    async def run_wave(
        self,
        service_ids: list[str],
        *,
        wave_id: str,
        publish: bool = True,
    ) -> dict[str, Any]:
        results: list[DeepResearchServiceResult] = []
        for sid in service_ids:
            results.append(self.research_service(sid))

        staging_path = self.build_staging(service_ids)
        pub_report: dict[str, Any] = {"skipped": not publish}
        if publish:
            pub_report = self.publish_to_runtime(dry_run=False)

        runtime_report = await self.validate_runtime(service_ids)
        for r in results:
            svc_runtime = next(
                (s for s in runtime_report.get("services") or [] if s.get("catalogue_service_id") == r.service_id),
                {},
            )
            r.runtime_publication = {
                "published_claim_count": svc_runtime.get("published_claim_count", 0),
                "verified_published_claim_count": svc_runtime.get("verified_published_claim_count", 0),
            }
            r.retrieval_accuracy = float(svc_runtime.get("retrieval_accuracy") or 0)
            if (svc_runtime.get("published_claim_count") or 0) == 0 and publish:
                r.issues.append("PUBLICATION_NO_CLAIMS")
            if r.retrieval_accuracy < self.RETRIEVAL_ACCURACY_TARGET:
                r.issues.append("RETRIEVAL_BELOW_TARGET")

        gate = self.evaluate_wave_gate(results, wave_id)
        wave_doc = {
            "wave_id": wave_id,
            "generated_at": _now(),
            "service_ids": service_ids,
            "staging_path": str(staging_path),
            "publication": pub_report,
            "runtime": runtime_report,
            "results": [asdict(r) for r in results],
            "gate": asdict(gate),
        }
        wave_path = self.output_root / f"{wave_id}.json"
        self.output_root.mkdir(parents=True, exist_ok=True)
        wave_path.write_text(json.dumps(wave_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return wave_doc

    async def run_pilot(
        self,
        wave1_ids: list[str],
        wave2_ids: list[str],
        *,
        publish: bool = True,
    ) -> dict[str, Any]:
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.eval_root.mkdir(parents=True, exist_ok=True)

        wave1 = await self.run_wave(wave1_ids, wave_id="wave-01", publish=publish)
        gate1 = wave1["gate"]
        wave2 = await self.run_wave(wave2_ids, wave_id="wave-02", publish=publish)
        regression = self.run_regression()
        final_gate = self.evaluate_wave_gate(
            [DeepResearchServiceResult(**r) for r in wave1["results"] + wave2["results"]],
            "final-pilot-gate",
        )

        summary = {
            "generated_at": _now(),
            "pilot": PILOT_OUTPUT,
            "wave1": wave1,
            "wave2": wave2,
            "wave1_gate_passed": gate1["passed"],
            "wave2_gate_passed": wave2["gate"]["passed"],
            "final_gate": asdict(final_gate),
            "regression": regression,
            "aggregate": {
                "services": len(wave1_ids) + len(wave2_ids),
                "avg_supported_coverage": round(
                    (
                        gate1["avg_supported_coverage"] * len(wave1_ids)
                        + wave2["gate"]["avg_supported_coverage"] * len(wave2_ids)
                    )
                    / max(len(wave1_ids) + len(wave2_ids), 1),
                    4,
                ),
                "avg_retrieval_accuracy": round(
                    (
                        gate1["avg_retrieval_accuracy"] * len(wave1_ids)
                        + wave2["gate"]["avg_retrieval_accuracy"] * len(wave2_ids)
                    )
                    / max(len(wave1_ids) + len(wave2_ids), 1),
                    4,
                ),
            },
            "pilot_passed": final_gate.passed and regression["regression_passed"],
            "step31_excluded": sorted(STEP31_EXCLUDED),
            "bottleneck_summary": self._summarize_bottlenecks(wave1, wave2),
        }
        summary_path = self.output_root / "pilot-summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return summary

    def _summarize_bottlenecks(self, wave1: dict[str, Any], wave2: dict[str, Any]) -> dict[str, Any]:
        layers = {
            "PUBLICATION": 0,
            "RETRIEVAL": 0,
            "RESEARCH": 0,
        }
        for wave in (wave1, wave2):
            for svc in (wave.get("runtime") or {}).get("services") or []:
                if "PUBLICATION_GATE_BLOCKED" in (svc.get("issues") or []):
                    layers["PUBLICATION"] += 1
                if (svc.get("retrieval_accuracy") or 0) < self.RETRIEVAL_ACCURACY_TARGET:
                    layers["RETRIEVAL"] += 1
            for b in (wave.get("runtime") or {}).get("bottlenecks") or []:
                layer = b.get("layer", "OTHER")
                layers[layer] = layers.get(layer, 0) + int(b.get("count") or 0)
        primary = max(layers, key=lambda k: layers[k]) if any(layers.values()) else "NONE"
        return {"primary_bottleneck": primary, "layer_counts": layers}


def run_pilot_sync(wave1: list[str], wave2: list[str], *, publish: bool = True) -> dict[str, Any]:
    pipeline = DeepResearchPipeline(Path(__file__).resolve().parents[2])
    return asyncio.run(pipeline.run_pilot(wave1, wave2, publish=publish))
