#!/usr/bin/env python3
"""Mark remaining PARTIAL services as DEEP_RESEARCH_REQUIRED in rerun_queue.json."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEP31 = frozenset(
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


def main() -> int:
    audit = json.loads((ROOT / "data" / "audit" / "final-service-completeness.json").read_text())
    partial_ids = {
        s["service_id"]
        for s in audit.get("services") or []
        if s.get("completeness") == "PARTIAL"
    }

    pilot_path = ROOT / "data" / "research" / "deep-research-pilot-20" / "selection.json"
    pilot_ids: set[str] = set()
    if pilot_path.exists():
        pilot_ids = {s["service_id"] for s in json.loads(pilot_path.read_text()).get("services") or []}

    queue_path = ROOT / "data" / "research" / "rerun_queue.json"
    queue_doc = json.loads(queue_path.read_text(encoding="utf-8")) if queue_path.exists() else {"queue": []}

    catalogue = {}
    cat_path = ROOT / "data" / "service_catalogue" / "services.json"
    if cat_path.exists():
        doc = json.loads(cat_path.read_text())
        services = doc.get("services") if isinstance(doc, dict) else doc
        catalogue = {s["service_id"]: s for s in services if isinstance(s, dict) and s.get("service_id")}

    existing = {e["service_id"]: e for e in queue_doc.get("queue") or [] if e.get("service_id")}
    for sid in sorted(partial_ids - STEP31 - pilot_ids):
        entry = catalogue.get(sid) or {}
        existing[sid] = {
            "service_id": sid,
            "service_name_en": entry.get("service_name_en") or sid,
            "category_id": entry.get("category_id"),
            "batch_slug": entry.get("batch_slug") or "",
            "previous_status": "PARTIAL",
            "false_completion_reason": "partial_knowledge_gaps",
            "required_research_profile": entry.get("research_profile") or "OTHER",
            "priority": 40,
            "dependencies": [],
            "next_research_task": f"DEEP RESEARCH THIS EXACT SERVICE: {sid}",
            "target_status": "DEEP_RESEARCH_REQUIRED",
            "pipeline": "DEEP_RESEARCH",
            "do_not_autorun": True,
        }

    queue_doc["generated_at"] = datetime.now(timezone.utc).isoformat()
    queue_doc["total_partial_services"] = len(partial_ids)
    queue_doc["deep_research_required_count"] = sum(
        1 for e in existing.values() if e.get("target_status") == "DEEP_RESEARCH_REQUIRED"
    )
    queue_doc["do_not_autorun_until_pilot_passes"] = True
    queue_doc["pilot_20_service_ids"] = sorted(pilot_ids)
    queue_doc["step31_excluded_service_ids"] = sorted(STEP31)
    queue_doc["queue"] = list(existing.values())

    queue_path.write_text(json.dumps(queue_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "deep_research_required": queue_doc["deep_research_required_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
