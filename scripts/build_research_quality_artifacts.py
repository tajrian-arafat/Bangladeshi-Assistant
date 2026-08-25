#!/usr/bin/env python3
"""Generate research quality audit artifacts: detection, rerun queue, runtime DB diagnostic."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_audit_services() -> list[dict[str, Any]]:
    path = ROOT / "data" / "audit" / "final-service-completeness.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc.get("services") or []


def build_rerun_queue(services: list[dict[str, Any]]) -> dict[str, Any]:
    from automation.orchestrator.research_quality import load_profiles, resolve_profile_key

    profiles_doc = load_profiles(ROOT)
    catalogue = {
        s.get("service_id") or s.get("id"): s
        for s in json.loads((ROOT / "data" / "service_catalogue" / "services.json").read_text(encoding="utf-8")).get(
            "services", []
        )
    }

    queue_items: list[dict[str, Any]] = []
    for svc in services:
        flags = svc.get("flags") or []
        if "FALSE_COMPLETION_RISK" not in flags and svc.get("completeness") != "FALSE_COMPLETION_RISK":
            continue
        sid = svc.get("service_id", "")
        entry = catalogue.get(sid) or {}
        profile_key = resolve_profile_key(entry, profiles_doc)

        reasons: list[str] = []
        if svc.get("boilerplate_claims", 0) >= 2:
            reasons.append("generic_boilerplate_claims")
        if svc.get("service_specific_claims", 0) == 0:
            reasons.append("no_service_specific_claims")
        if "GENERIC_BUILDER_BATCH" in flags:
            reasons.append("generic_builder_batch")
        if svc.get("catalogue_only_sources"):
            reasons.append("catalogue_only_sources")

        priority = 100
        if svc.get("category_id") in {"land", "health", "tax", "vat", "passport", "transport"}:
            priority -= 30
        if svc.get("boilerplate_claims", 0) == svc.get("total_claims", 0):
            priority -= 20
        if "WRONG_SOURCE_BLEED" in flags or any("nbr" in str(r).lower() for r in reasons):
            priority -= 15

        queue_items.append(
            {
                "service_id": sid,
                "service_name_en": svc.get("service_name_en"),
                "category_id": svc.get("category_id"),
                "batch_slug": svc.get("batch_slug"),
                "previous_status": svc.get("completeness", "PARTIAL"),
                "false_completion_reason": "; ".join(reasons) or "metadata_only_research",
                "required_research_profile": profile_key,
                "priority": priority,
                "dependencies": [],
                "current_sources": svc.get("tier1_2_sources", 0),
                "current_claims": svc.get("total_claims", 0),
                "next_research_task": f"RESEARCH THIS EXACT SERVICE: {sid}",
                "target_status": "RESEARCH_REQUIRED",
            }
        )

    queue_items.sort(key=lambda x: x["priority"])

    return {
        "generated_at": _now(),
        "total_false_completion_services": len(queue_items),
        "do_not_autorun_until_pilot_passes": True,
        "pilot_service_ids": [
            "land-deed-registration",
            "education-class-registration",
            "health-16263-telemedicine",
            "ff-g2p-electronic-payment",
            "disability-dis-registration",
            "vat-bin-registration",
            "dc-attestation-photocopy",
            "judiciary-case-status-tracking",
            "agri-bamis-farmer-registration",
            "employment-boesl-overseas-recruitment",
        ],
        "queue": queue_items,
    }


def diagnose_runtime_database() -> dict[str, Any]:
    candidates = [
        ROOT / "data" / "bda.db",
        ROOT / "backend" / "data" / "bda.db",
        ROOT / "backend" / "bda.db",
    ]
    env_db = __import__("os").environ.get("DATABASE_URL", "")

    findings: list[dict[str, Any]] = []
    primary_path = ROOT / "data" / "bda.db"

    for path in candidates:
        if path.exists():
            size = path.stat().st_size
            findings.append({"path": str(path), "exists": True, "size_bytes": size})

    diagnosis = "UNKNOWN"
    explanation = ""
    recommendation = ""

    populated = [f for f in findings if f.get("size_bytes", 0) > 0]
    backend_populated = next((f for f in findings if "backend" in f["path"] and f.get("size_bytes", 0) > 0), None)

    if primary_path.exists() and primary_path.stat().st_size == 0 and backend_populated:
        diagnosis = "D_WRONG_AUDIT_PATH"
        explanation = (
            f"Audit path data/bda.db is empty (0 bytes) but populated database exists at "
            f"{backend_populated['path']} ({backend_populated['size_bytes']} bytes). "
            "Runtime knowledge may exist via backend path; final audit inspected the wrong canonical path."
        )
        recommendation = (
            "Align publication and audit on a single canonical runtime DB path. "
            "E2E/backend tests use backend/data/bda.db; do not treat empty data/bda.db alone as total absence of runtime knowledge."
        )
    elif primary_path.exists() and primary_path.stat().st_size == 0:
        diagnosis = "B_EMPTY_FILE"
        explanation = (
            "Runtime database file exists at data/bda.db but is 0 bytes. "
            "Publication has not populated runtime knowledge, or the audit environment "
            "never ran publish_verified_knowledge against a seeded database."
        )
        recommendation = (
            "Do not claim runtime knowledge is available. Run publication with deployment lock "
            "after verified staging knowledge exists; verify non-zero bda.db with service rows."
        )
    elif not primary_path.exists():
        diagnosis = "A_NOT_PRESENT"
        explanation = "Runtime DB file not found at expected path."
        recommendation = "Initialize database via backend migrations and publish verified knowledge."
    else:
        try:
            conn = sqlite3.connect(str(primary_path))
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            conn.close()
            diagnosis = "OK_POPULATED"
            explanation = f"Runtime DB has tables: {tables[:10]}"
        except Exception as exc:
            diagnosis = "E_CORRUPT_OR_INVALID"
            explanation = str(exc)

    publish_script = ROOT / "scripts" / "publish_verified_knowledge.py"
    staging_count = len(list((ROOT / "data" / "research" / "staging").glob("*/claims.json")))

    return {
        "generated_at": _now(),
        "diagnosis_code": diagnosis,
        "diagnosis": explanation,
        "recommendation": recommendation,
        "database_url_env": env_db or None,
        "files_inspected": findings,
        "staging_batches_with_claims": staging_count,
        "publication_script_exists": publish_script.exists(),
        "deployment_locked": not (ROOT / ".automation" / "deployment.lock").exists()
        or (ROOT / ".automation" / "deployment.lock").read_text().strip().lower() not in {"true", "1", "yes"},
        "runtime_knowledge_available": diagnosis in {"OK_POPULATED", "D_WRONG_AUDIT_PATH"},
        "populated_database_path": populated[0]["path"] if populated else None,
        "verdict": (
            "Runtime knowledge available at alternate backend path"
            if diagnosis == "D_WRONG_AUDIT_PATH"
            else ("Runtime knowledge available" if diagnosis == "OK_POPULATED" else "Runtime knowledge NOT available at audit path")
        ),
    }


def main() -> None:
    from automation.orchestrator.research_quality import detect_generic_claims_across_services

    services = load_audit_services()

    detection = detect_generic_claims_across_services(ROOT, services)
    _write_json(ROOT / "data" / "audit" / "generic-claim-detection.json", detection)

    rerun = build_rerun_queue(services)
    _write_json(ROOT / "data" / "research" / "rerun_queue.json", rerun)

    runtime_diag = diagnose_runtime_database()
    _write_json(ROOT / "data" / "audit" / "runtime-database-diagnostic.json", runtime_diag)

    print(f"generic-claim-detection: {detection['classification_counts']}")
    print(f"rerun_queue: {rerun['total_false_completion_services']} services")
    print(f"runtime_db: {runtime_diag['diagnosis_code']} — {runtime_diag['verdict']}")


if __name__ == "__main__":
    main()
