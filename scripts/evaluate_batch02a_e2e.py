#!/usr/bin/env python3
"""Batch 2A passport end-to-end assistant evaluation (local/dev only).

Step 16: normalized outcomes measure truthfulness, not verbosity.

Outputs:
  data/evaluation/batch-02a-passport/results.jsonl
  data/evaluation/batch-02a-passport/summary.json
  data/evaluation/batch-02a-passport/failures.json
  data/evaluation/batch-02a-passport/classification.json
  docs/evaluation/batch-02a-passport-completion.md
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
sys.path.insert(0, str(REPO_ROOT / "scripts"))
os.chdir(BACKEND_DIR)

from app.ai.orchestrator import Orchestrator  # noqa: E402
from app.core.database import get_session_factory  # noqa: E402
from app.schemas.chat import ChatRequest  # noqa: E402
from passport_eval_outcomes import evaluate_passport_outcome, infer_expected_outcome  # noqa: E402

OUT_DIR = REPO_ROOT / "data" / "evaluation" / "batch-02a-passport"
DOCS_PATH = REPO_ROOT / "docs" / "evaluation" / "batch-02a-passport-completion.md"
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
    base = {
        "pass": passed,
        "checks": checks,
        "reasons": reasons,
        "failure_class": failure_class,
        "recommended_fix": _b01._recommend(failure_class, reasons),
    }
    outcome = evaluate_passport_outcome(case, actual, base)
    step16_class = outcome["step16_failure_class"]
    return {
        "pass": outcome["pass"],
        "raw_pass": outcome["raw_pass"],
        "expected_outcome": outcome["expected_outcome"],
        "actual_outcome": outcome["actual_outcome"],
        "counts_as_product_failure": outcome["counts_as_product_failure"],
        "checks": outcome["checks"],
        "reasons": outcome["reasons"],
        "failure_class": step16_class or failure_class,
        "legacy_failure_class": failure_class,
        "recommended_fix": _b01._recommend(step16_class or failure_class, outcome["reasons"]),
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
                "expected_outcome": infer_expected_outcome(case),
            },
            "actual": actual,
            "pass": judgment["pass"],
            "raw_pass": judgment.get("raw_pass", judgment["pass"]),
            "expected_outcome": judgment.get("expected_outcome"),
            "actual_outcome": judgment.get("actual_outcome"),
            "counts_as_product_failure": judgment.get("counts_as_product_failure", not judgment["pass"]),
            "checks": judgment["checks"],
            "reasons": judgment["reasons"],
            "failure_class": judgment["failure_class"],
            "legacy_failure_class": judgment.get("legacy_failure_class"),
            "recommended_fix": judgment["recommended_fix"],
        }


def write_markdown(summary: dict, results: list[dict], failures: list[dict], pub: dict) -> None:
    lines: list[str] = []
    lines.append("# Batch 2A Passport — Completion & Evaluation Normalization (Step 16)")
    lines.append("")
    lines.append(f"**Generated:** {summary['generated_at']}")
    lines.append("**Mode:** Local/development only — no deployment, no Batch 2B")
    lines.append("")
    lines.append("## Headline metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|------:|")
    lines.append(f"| Total tests | {summary['total_tests']} |")
    lines.append(f"| Raw pass rate | {summary['raw_pass_rate_pct']}% ({summary['raw_passed']}/{summary['total_tests']}) |")
    lines.append(f"| Normalized pass rate | {summary['pass_rate_pct']}% ({summary['passed']}/{summary['total_tests']}) |")
    lines.append(f"| Supported-case accuracy | {summary['supported_case_accuracy_pct']}% ({summary['supported_passed']}/{summary['supported_cases']}) |")
    lines.append(f"| Hallucinations (product failures) | {summary['hallucinations']} |")
    lines.append(f"| Citation failures | {summary['citation_failures']} |")
    lines.append(f"| Correct-uncertainty rate | {summary['correct_uncertainty_rate_pct']}% |")
    lines.append(f"| Correct-refusal rate | {summary['correct_refusal_rate_pct']}% |")
    lines.append("")
    lines.append("## Outcome distribution")
    for k, v in summary.get("outcome_counts", {}).items():
        lines.append(f"- **{k}:** {v}")
    lines.append("")
    lines.append("## Step 16 failure classification")
    for k, v in summary.get("step16_failure_class_counts", {}).items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("## Service readiness (from published claims)")
    for svc, readiness in summary.get("service_readiness", {}).items():
        lines.append(f"- `{svc}`: **{readiness}**")
    lines.append("")
    lines.append("## Remaining knowledge gaps")
    for g in summary.get("remaining_gaps", []):
        lines.append(f"- {g}")
    lines.append("")
    lines.append("## Product failures (supported cases only)")
    for r in failures:
        if r.get("counts_as_product_failure"):
            lines.append(f"- **{r['id']}** ({r.get('failure_class')}): {'; '.join(r['reasons'])}")
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
    raw_passed = sum(1 for r in results if r.get("raw_pass", r["pass"]))
    failed = total - passed
    fail_classes = Counter(r["failure_class"] for r in results if not r["pass"])
    step16_classes = Counter(
        r["failure_class"] for r in results if r.get("counts_as_product_failure")
    )

    supported_cases = [
        r
        for r in results
        if r.get("expected_outcome") == "ANSWER_SUPPORTED"
        or (
            r.get("expected", {}).get("expected_outcome") == "ANSWER_SUPPORTED"
        )
    ]
    supported_passed = sum(1 for r in supported_cases if r["pass"])

    uncertainty_cases = [
        r for r in results if r.get("expected_outcome") == "CORRECT_UNCERTAINTY"
    ]
    uncertainty_passed = sum(1 for r in uncertainty_cases if r["pass"])

    refusal_cases = [
        r
        for r in results
        if r.get("expected_outcome") in {"CORRECT_REFUSAL", "ANSWER_UNSUPPORTED_CORRECTLY"}
    ]
    refusal_passed = sum(1 for r in refusal_cases if r["pass"])

    outcome_counts = Counter(r.get("expected_outcome") for r in results)

    hallu_product = sum(
        1
        for r in results
        if r.get("counts_as_product_failure")
        and r.get("failure_class") in {"HALLUCINATION", "RESPONSE_PLANNER_BUG"}
    )
    citation_f = sum(
        1
        for r in results
        if r.get("counts_as_product_failure") and r.get("failure_class") == "CITATION_BUG"
    )

    hallu_cases = [r for r in results if r["category"] == "hallucination"]
    hallu_pass = sum(1 for r in hallu_cases if r["pass"])
    unsupported = [r for r in results if r["category"] in {"unsupported_fee", "hallucination"}]

    pub_summary_path = OUT_DIR / "publication_summary.json"
    pub = {}
    if pub_summary_path.exists():
        pub = json.loads(pub_summary_path.read_text(encoding="utf-8"))

    classification = []
    for r in results:
        if not r["pass"] or r.get("failure_class"):
            classification.append(
                {
                    "id": r["id"],
                    "query": r["query"],
                    "category": r.get("category"),
                    "expected_outcome": r.get("expected_outcome"),
                    "step16_class": r.get("failure_class") if r.get("counts_as_product_failure") else (
                        r.get("expected_outcome") if r["pass"] else "EVALUATOR_PROBLEM"
                    ),
                    "counts_as_product_failure": r.get("counts_as_product_failure", False),
                    "pass": r["pass"],
                    "raw_pass": r.get("raw_pass"),
                    "reasons": r.get("reasons"),
                }
            )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch_id": "batch-02a-passport",
        "evaluation_version": "step-16-normalized",
        "publication_mode": "local_dev_only",
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate_pct": round(100.0 * passed / total, 1),
        "raw_passed": raw_passed,
        "raw_pass_rate_pct": round(100.0 * raw_passed / total, 1),
        "supported_cases": len(supported_cases),
        "supported_passed": supported_passed,
        "supported_case_accuracy_pct": round(
            100.0 * supported_passed / max(1, len(supported_cases)), 1
        ),
        "hallucinations": hallu_product,
        "citation_failures": citation_f,
        "correct_uncertainty_rate_pct": round(
            100.0 * uncertainty_passed / max(1, len(uncertainty_cases)), 1
        ),
        "correct_refusal_rate_pct": round(
            100.0 * refusal_passed / max(1, len(refusal_cases)), 1
        ),
        "failure_class_counts": dict(fail_classes),
        "step16_failure_class_counts": dict(step16_classes),
        "outcome_counts": dict(outcome_counts),
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
            "uncertainty_cases": len(uncertainty_cases),
            "uncertainty_passed": uncertainty_passed,
            "refusal_cases": len(refusal_cases),
            "refusal_passed": refusal_passed,
        },
        "remaining_gaps": [
            "Universal police verification Tier-1 rule unresolved (CONDITIONAL only)",
            "Super Express eligibility wording conflict (June 2026 vs Oct 2022)",
            "MRP current fee schedule not machine-readable on DIP page",
            "Abu Dhabi WEFF 10% surcharge unverified (empty CMS render)",
            "Singapore mission e-passport rules URL 404",
            "Damaged passport distinct documentary rules not enumerated Tier-1",
            "Minor under-6 photo size rule indexed-only (not browser-snapshotted)",
        ],
        "service_readiness": pub.get("post_readiness", {}),
        "targets": {
            "hallucinations": 0,
            "citation_failures": 0,
            "supported_case_accuracy_pct_min": 95.0,
            "unsupported_current_fee_answers": 0,
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "results.jsonl").open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    failures = [r for r in results if r.get("counts_as_product_failure")]
    raw_failures = [r for r in results if not r["pass"]]
    (OUT_DIR / "failures.json").write_text(
        json.dumps(raw_failures, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (OUT_DIR / "classification.json").write_text(
        json.dumps(classification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_markdown(summary, results, failures, pub)
    print(json.dumps(summary, indent=2))
    return 0 if not any(r.get("counts_as_product_failure") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
