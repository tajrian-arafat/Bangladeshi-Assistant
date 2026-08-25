#!/usr/bin/env python3
"""Run 12-service deep-research pilot for partial-knowledge depth analysis."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from automation.orchestrator.deep_research_builder import DeepResearchBuilder
from automation.orchestrator.partial_knowledge_analyzer import PartialKnowledgeAnalyzer
from automation.orchestrator.phase_executor import PhaseExecutor


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_staging(pilot_results: list[dict]) -> Path:
    staging = ROOT / "data" / "research" / "deep-research-pilot" / "staging"
    staging.mkdir(parents=True, exist_ok=True)
    all_claims = []
    all_sources = []
    for r in pilot_results:
        svc_dir = Path(r["output_dir"])
        claims = json.loads((svc_dir / "claims.json").read_text(encoding="utf-8")).get("claims") or []
        sources = json.loads((svc_dir / "sources.json").read_text(encoding="utf-8")).get("sources") or []
        for c in claims:
            if c.get("claim_class") == "SERVICE_SPECIFIC" and c.get("verification_status") == "VERIFIED":
                all_claims.append(c)
        all_sources.extend(s for s in sources if s.get("source_id") != "src-catalogue")
    (staging / "claims.json").write_text(json.dumps({"claims": all_claims}, indent=2) + "\n", encoding="utf-8")
    (staging / "sources.json").write_text(json.dumps({"sources": all_sources}, indent=2) + "\n", encoding="utf-8")
    (staging / "metadata.json").write_text(
        json.dumps({"pilot": "deep-research", "services": [r["service_id"] for r in pilot_results], "published_at": _now()}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return staging


def validate_runtime_db(service_ids: list[str]) -> dict:
    db_path = ROOT / "backend" / "data" / "bda.db"
    result = {"db_path": str(db_path), "exists": db_path.exists(), "size_bytes": db_path.stat().st_size if db_path.exists() else 0}
    if not db_path.exists():
        result["status"] = "DB_MISSING"
        return result
    try:
        import sqlite3

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        result["tables"] = tables
        for sid in service_ids[:3]:
            try:
                cur.execute("SELECT COUNT(*) FROM claims WHERE service_id = ?", (sid,))
                result.setdefault("sample_claim_counts", {})[sid] = cur.fetchone()[0]
            except Exception:
                pass
        conn.close()
        result["status"] = "RUNTIME_DB_ACCESSIBLE"
    except Exception as exc:
        result["status"] = "RUNTIME_CHECK_ERROR"
        result["error"] = str(exc)
    return result


def run_regression() -> dict:
    executor = PhaseExecutor(ROOT)
    batch = {"batch_id": "DEEP_RESEARCH_PILOT", "slug": "deep-research-pilot", "service_ids": []}
    result = executor.execute_regression(run_id="deep-research-pilot-regression", batch=batch)
    auto = subprocess.run(
        [sys.executable, "-m", "pytest", "automation/tests", "backend/tests", "-q", "--tb=no"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    return {
        "regression_passed": result.status == "SUCCESS" and auto.returncode == 0,
        "regression_status": result.status,
        "automation_backend_tests": auto.returncode == 0,
        "automation_output_tail": auto.stdout.splitlines()[-3:] if auto.stdout else [],
    }


def main() -> int:
    analyzer = PartialKnowledgeAnalyzer(ROOT)
    pilot_services = analyzer.select_pilot_services()
    if len(pilot_services) < 12:
        print(json.dumps({"error": "Insufficient pilot services", "selected": pilot_services}, indent=2))
        return 1

    builder = DeepResearchBuilder(ROOT)
    pilot_results: list[dict] = []

    for svc in pilot_services:
        service_id = svc["service_id"]
        before_eval = None
        rerun_dir = ROOT / "data" / "research" / "rerun"
        for wave_dir in sorted(rerun_dir.iterdir(), reverse=True) if rerun_dir.is_dir() else []:
            eval_file = ROOT / "data" / "evaluation" / "waves" / wave_dir.name / f"{service_id}.json"
            if eval_file.exists():
                before_eval = json.loads(eval_file.read_text(encoding="utf-8"))
                break

        deep = builder.build_deep_research(service_id)
        verification = builder.verify_deep_claims(service_id)
        e2e = builder.run_deep_e2e(service_id, verification["verification_map"])
        after_eval = builder.evaluate_before_after(service_id, e2e, verification["verification_map"])

        pilot_results.append(
            {
                "service_id": service_id,
                "pilot_role": svc["pilot_role"],
                "output_dir": deep["output_dir"],
                "before": {
                    "meaningful_claims": deep.get("before_meaningful_claims", 0),
                    "supported_answer_coverage": before_eval.get("answer_supported", 0) / max(before_eval.get("total", 1), 1) if before_eval else 0,
                },
                "after": {
                    "meaningful_claims": deep.get("after_meaningful_claims", 0),
                    "verified_claims": after_eval.get("verified_claims", 0),
                    "supported_answer_coverage": e2e.get("supported_answer_coverage", 0),
                    "completeness_score": after_eval.get("completeness_score", 0),
                    "research_status": after_eval.get("research_status"),
                    "missing_dimensions": after_eval.get("missing_dimensions", []),
                },
                "e2e": e2e,
                "evaluation": after_eval,
            }
        )

    staging = build_staging(pilot_results)
    runtime = validate_runtime_db([r["service_id"] for r in pilot_results])
    regression = run_regression()

    summary = {
        "generated_at": _now(),
        "pilot_services": pilot_services,
        "results": pilot_results,
        "staging_path": str(staging),
        "runtime_validation": runtime,
        "regression": regression,
        "aggregate": {
            "avg_supported_coverage_before": round(
                sum(r["before"]["supported_answer_coverage"] for r in pilot_results) / len(pilot_results), 4
            ),
            "avg_supported_coverage_after": round(
                sum(r["after"]["supported_answer_coverage"] for r in pilot_results) / len(pilot_results), 4
            ),
            "avg_verified_claims_after": round(
                sum(r["after"]["verified_claims"] for r in pilot_results) / len(pilot_results), 2
            ),
        },
    }

    out_path = ROOT / "data" / "research" / "deep-research-pilot" / "pilot-summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Generate markdown report
    from scripts.generate_partial_depth_report import generate_report

    generate_report(ROOT, summary)

    print(json.dumps({"ok": True, "pilot_services": len(pilot_results), "regression_passed": regression["regression_passed"]}, indent=2))
    return 0 if regression["regression_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
