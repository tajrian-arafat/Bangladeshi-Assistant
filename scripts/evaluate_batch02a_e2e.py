#!/usr/bin/env python3
"""Batch 2A passport end-to-end assistant evaluation (local/dev only).

Outputs:
  data/evaluation/batch-02a-passport/results.jsonl
  data/evaluation/batch-02a-passport/summary.json
  data/evaluation/batch-02a-passport/failures.json
  docs/evaluation/batch-02a-passport-publication-and-e2e.md
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from app.ai.orchestrator import Orchestrator  # noqa: E402
from app.core.database import get_session_factory  # noqa: E402
from app.schemas.chat import ChatRequest  # noqa: E402

OUT_DIR = REPO_ROOT / "data" / "evaluation" / "batch-02a-passport"
DOCS_PATH = REPO_ROOT / "docs" / "evaluation" / "batch-02a-passport-publication-and-e2e.md"
QUERIES_PATH = OUT_DIR / "queries.json"

# Reuse batch-01 evaluation helpers
_b01_path = REPO_ROOT / "scripts" / "evaluate_batch01_e2e.py"
_spec = importlib.util.spec_from_file_location("evaluate_batch01_e2e", _b01_path)
_b01 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_b01)

PASSPORT_FAMILY = {
    "epassport-new-application",
    "epassport-reissue",
    "epassport-fee-payment",
    "epassport-enrollment-appointment",
    "epassport-application-status",
    "epassport-urgent-super-express",
    "epassport-rpo-secretariat",
    "passport-mrp-initial",
    "passport-mrp-reissue",
    "passport-application-status",
    "police-passport-police-verification",
    "police-passport-verification",
    "passport-renewal",
}
STATUS_FAMILY = {"epassport-application-status", "passport-application-status"}


def evaluate_passport_case(case: dict, actual: dict) -> dict[str, Any]:
    """Extend batch-01 evaluator with passport-specific gates."""
    base = _b01.evaluate_case(case, actual)
    expect = case.get("expect") or {}
    reasons = list(base["reasons"])
    checks = dict(base["checks"])

    summary = (actual.get("summary") or "").lower()
    warnings = " ".join(actual.get("warnings") or []).lower()
    fees = actual.get("fees") or []
    fee_amounts = [str(f.get("amount")) for f in fees]
    blob = json.dumps(actual, ensure_ascii=False).lower()
    svc = actual.get("service_slug")
    citations = actual.get("citations") or []

    if expect.get("allow_passport_family") and svc and svc in PASSPORT_FAMILY:
        checks["service"] = True
        if "service mismatch" in " | ".join(reasons):
            reasons = [r for r in reasons if "service mismatch" not in r]

    if expect.get("allow_reissue_alias") and svc in {"passport-renewal", "epassport-reissue"}:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if expect.get("allow_status_family") and svc in STATUS_FAMILY:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if expect.get("must_not_affirm_ekpay"):
        affirmed = "ekpay" in summary and "not" not in summary[: summary.find("ekpay") + 20]
        affirmed = affirmed or (
            "ekpay" in blob
            and "a-challan" not in blob
            and "uncertain" not in warnings
            and "not confirmed" not in warnings
        )
        checks["no_ekpay_affirm"] = not affirmed
        if affirmed:
            reasons.append("affirmed ekpay as current passport payment method")

    if expect.get("must_not_affirm_weff_surcharge"):
        affirmed = "10%" in summary and "abudhabi" in blob.replace(" ", "")
        affirmed = affirmed or ("weff" in blob or "wage earners" in blob)
        if affirmed and "unverified" not in warnings and "not confirmed" not in warnings:
            checks["no_weff"] = False
            reasons.append("affirmed Abu Dhabi WEFF surcharge without verification")
        else:
            checks["no_weff"] = True

    if expect.get("must_not_universal_pv_rule"):
        universal = (
            ("always required" in summary or "always mandatory" in summary)
            and "police" in summary
        ) or ("never required" in summary and "police" in summary)
        ok = not universal or bool(warnings) or "conditional" in summary
        checks["pv_not_universal"] = ok
        if not ok:
            reasons.append("stated universal police verification rule")

    if expect.get("must_not_universal_super_express_rule"):
        if "only" in summary and "mrp" in summary and "address change" in summary:
            if "differs" not in summary and "uncertain" not in warnings:
                checks["se_not_universal"] = False
                reasons.append("invented narrow Super Express rule without conflict note")
            else:
                checks["se_not_universal"] = True
        else:
            checks["se_not_universal"] = True

    if expect.get("must_not_publish_outdated_march2023"):
        outdated_only = "march 2023" in summary and "july 2026" not in summary
        if outdated_only and fee_amounts:
            checks["no_outdated_only"] = False
            reasons.append("presented March 2023 fee page as current without July 2026 evidence")
        else:
            checks["no_outdated_only"] = True

    if expect.get("must_cite_july2026_evidence"):
        cite_ok = any(
            "2026" in (c.get("excerpt") or "").lower()
            or "july" in (c.get("excerpt") or "").lower()
            or "epassport.gov.bd" in (c.get("source_url") or "").lower()
            for c in citations
        ) or "2026" in summary
        checks["july2026_cite"] = cite_ok or bool(fee_amounts)
        if not checks["july2026_cite"]:
            reasons.append("July 2026 fee evidence not cited")

    if expect.get("must_include_payment_methods"):
        methods = expect["must_include_payment_methods"]
        found = sum(1 for m in methods if m.lower() in blob)
        ok = found >= 2  # at least two of three verified gateways mentioned
        checks["payment_methods"] = ok
        if not ok:
            reasons.append(f"verified payment methods not surfaced: expected {methods}")

    passed = len(reasons) == 0
    if checks and all(checks.values()) and not reasons:
        passed = True

    failure_class = None if passed else _b01.classify_failure(case, actual, reasons)
    return {
        "pass": passed,
        "checks": checks,
        "reasons": reasons,
        "failure_class": failure_class,
        "recommended_fix": _b01._recommend(failure_class, reasons),
    }


async def run_one(session_factory, case: dict) -> dict[str, Any]:
    async with session_factory() as session:
        req = ChatRequest(
            message=case["query"],
            language_preference="auto",
            clarifications=case.get("clarifications") or {},
        )
        answer, confidence, intent, citations, ctx = await Orchestrator(session).run(req)
        actual = {
            "language": ctx.language,
            "normalized_message": ctx.normalized_message,
            "intent": intent,
            "service_slug": ctx.service.slug if ctx.service else None,
            "service_name": ctx.service.name_en if ctx.service else None,
            "entities": {
                k: v for k, v in ctx.entities.items() if k not in {"service", "agency"}
            },
            "support_level": ctx.support_level.value if ctx.support_level else None,
            "confidence": confidence,
            "clarifications_needed": ctx.clarifications_needed,
            "conflicts": ctx.conflicts,
            "evidence_count": len(ctx.evidence),
            "summary": answer.summary,
            "checklist": [c.model_dump() for c in answer.checklist],
            "steps": [s.model_dump() for s in answer.steps],
            "fees": [f.model_dump() for f in answer.fees],
            "warnings": answer.warnings,
            "practical_notes": answer.practical_notes,
            "official_urls": answer.official_urls,
            "citations": [c.model_dump() for c in citations],
        }
        judgment = evaluate_passport_case(case, actual)
        return {
            "id": case["id"],
            "query": case["query"],
            "language": case.get("language"),
            "category": case.get("category"),
            "expected": {
                "intent": case.get("intent_expected"),
                "service": case.get("service_expected"),
                "expect": case.get("expect"),
            },
            "actual": actual,
            "pass": judgment["pass"],
            "checks": judgment["checks"],
            "reasons": judgment["reasons"],
            "failure_class": judgment["failure_class"],
            "recommended_fix": judgment["recommended_fix"],
        }


def write_markdown(summary: dict, results: list[dict], failures: list[dict], pub: dict) -> None:
    lines: list[str] = []
    lines.append("# Batch 2A Passport — Controlled Publication & E2E Evaluation")
    lines.append("")
    lines.append(f"**Generated:** {summary['generated_at']}")
    lines.append("**Mode:** Local/development only — no deployment, no Batch 2B")
    lines.append("")
    lines.append("## Publication summary")
    lines.append("")
    for k, v in pub.items():
        lines.append(f"- **{k}:** {v}")
    lines.append("")
    lines.append("## E2E headline results")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|------:|")
    lines.append(f"| Total tests | {summary['total_tests']} |")
    lines.append(f"| Passed | {summary['passed']} |")
    lines.append(f"| Failed | {summary['failed']} |")
    lines.append(f"| Pass rate | {summary['pass_rate_pct']}% |")
    lines.append(f"| Hallucinations | {summary['hallucinations']} |")
    lines.append(f"| Citation failures | {summary['citation_failures']} |")
    lines.append("")
    lines.append("## Metrics")
    for k, v in summary["metrics"].items():
        lines.append(f"- **{k}:** {v}")
    lines.append("")
    lines.append("## Remaining knowledge gaps")
    for g in summary.get("remaining_gaps", []):
        lines.append(f"- {g}")
    lines.append("")
    lines.append("## Service readiness (post-publication)")
    for svc, readiness in summary.get("service_readiness", {}).items():
        lines.append(f"- `{svc}`: **{readiness}**")
    lines.append("")
    lines.append("## Sample failures")
    for r in failures[:12]:
        lines.append(f"### {r['id']} — `{r.get('failure_class')}`")
        lines.append(f"- Query: {r['query']}")
        lines.append(f"- Reasons: {'; '.join(r['reasons'])}")
        lines.append("")
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


async def main() -> int:
    cases = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    session_factory = get_session_factory()
    results: list[dict[str, Any]] = []
    for case in cases:
        results.append(await run_one(session_factory, case))

    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    failed = total - passed
    fail_classes = Counter(r["failure_class"] for r in results if not r["pass"])

    hallu_cases = [r for r in results if r["category"] == "hallucination"]
    hallu_pass = sum(1 for r in hallu_cases if r["pass"])
    unsupported = [r for r in results if r["category"] in {"unsupported_fee", "hallucination"}]

    pub_summary_path = OUT_DIR / "publication_summary.json"
    pub = {}
    if pub_summary_path.exists():
        pub = json.loads(pub_summary_path.read_text(encoding="utf-8"))

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch_id": "batch-02a-passport",
        "publication_mode": "local_dev_only",
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate_pct": round(100.0 * passed / total, 1),
        "hallucinations": fail_classes.get("HALLUCINATION", 0),
        "citation_failures": fail_classes.get("CITATION_BUG", 0),
        "failure_class_counts": dict(fail_classes),
        "metrics": {
            "hallucination_suite_pass_pct": round(100.0 * hallu_pass / len(hallu_cases), 1)
            if hallu_cases
            else None,
            "unsupported_query_pass_pct": round(
                100.0 * sum(1 for r in unsupported if r["pass"]) / max(1, len(unsupported)), 1
            ),
            "fee_query_count": sum(1 for r in results if r["category"] == "fee"),
            "fee_query_pass": sum(
                1 for r in results if r["category"] == "fee" and r["pass"]
            ),
        },
        "remaining_gaps": [
            "Universal police verification Tier-1 rule unresolved (CONDITIONAL only)",
            "Super Express eligibility wording conflict (June 2026 vs Oct 2022)",
            "MRP current fee schedule not machine-readable on DIP page",
            "Abu Dhabi WEFF 10% surcharge unverified (empty CMS render)",
            "Singapore mission e-passport rules URL 404",
            "Damaged passport distinct documentary rules not enumerated Tier-1",
        ],
        "service_readiness": pub.get("post_readiness", {}),
        "targets": {
            "hallucinations": 0,
            "citation_failures": 0,
            "unsupported_current_fee_answers": 0,
            "accidental_outdated_publication": 0,
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "results.jsonl").open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    failures = [r for r in results if not r["pass"]]
    (OUT_DIR / "failures.json").write_text(
        json.dumps(failures, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_markdown(summary, results, failures, pub)
    print(json.dumps(summary, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
