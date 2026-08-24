#!/usr/bin/env python3
"""Batch 1 end-to-end assistant evaluation harness.

Runs realistic queries through the full Orchestrator pipeline against local/dev DB.
Does NOT deploy. Does NOT start Batch 2.

Outputs:
  data/evaluation/batch-01/results.jsonl
  data/evaluation/batch-01/summary.json
  data/evaluation/batch-01/failures.json
  docs/evaluation/batch-01-end-to-end.md
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from app.ai.orchestrator import Orchestrator  # noqa: E402
from app.ai.routing.intent_canonical import intent_matches as canonical_intent_matches  # noqa: E402
from app.core.database import get_session_factory  # noqa: E402
from app.schemas.chat import ChatRequest  # noqa: E402

OUT_DIR = REPO_ROOT / "data" / "evaluation" / "batch-01"
DOCS_PATH = REPO_ROOT / "docs" / "evaluation" / "batch-01-end-to-end.md"
QUERIES_PATH = OUT_DIR / "queries.json"

NID_FAMILY = {
    "nid-correction",
    "nid-reissue-lost",
    "nid-card-info-correction",
    "nid-combined-correction",
    "nid-other-info-correction",
    "nid-fee-calculator",
    "nid-new-voter-registration",
    "nid-online-account-registration",
    "nid-claim-account",
    "nid-download-copy",
    "nid-photo-signature-appointment",
    "nid-voter-area-change",
    "nid-expatriate-registration",
}
BDRIS_FAMILY = {
    "birth-registration",
    "civil-birth-registration",
    "civil-birth-death-verify",
    "civil-birth-registration-copy",
    "civil-birth-registration-correction",
    "civil-birth-registration-duplicate-cancel",
    "civil-death-registration",
    "civil-death-registration-copy",
    "civil-death-registration-correction",
    "civil-bdris-application-print",
}


def classify_failure(case: dict, actual: dict, reasons: list[str]) -> str:
    joined = " | ".join(reasons).lower()
    if any("hallucin" in r.lower() or "affirmed rejected" in r.lower() or "static nid" in r.lower() or "fake url" in r.lower() for r in reasons):
        return "HALLUCINATION"
    if any("seed checklist" in r.lower() or "seed" in r.lower() for r in reasons):
        return "SEED_DATA_BUG"
    if any("service" in r.lower() for r in reasons):
        return "RETRIEVAL_BUG"
    if any("intent" in r.lower() for r in reasons):
        return "LANGUAGE_BUG" if case.get("language") in {"bn", "banglish"} else "OTHER"
    if any("citation" in r.lower() for r in reasons):
        return "CITATION_BUG"
    if any("practical" in r.lower() or "must need" in r.lower() or "conditional" in r.lower() for r in reasons):
        return "RULE_ENGINE_BUG"
    if any("fee" in r.lower() or "calculator" in r.lower() for r in reasons):
        return "CLAIM_SELECTION_BUG"
    if case.get("category") == "knowledge_gap" or "knowledge gap" in joined:
        return "KNOWLEDGE_GAP"
    if not actual.get("service_slug") and case.get("service_expected"):
        return "RETRIEVAL_BUG"
    return "OTHER"


def evaluate_case(case: dict, actual: dict) -> dict[str, Any]:
    expect = case.get("expect") or {}
    reasons: list[str] = []
    checks: dict[str, bool] = {}

    svc = actual.get("service_slug")
    intent = actual.get("intent")
    fees = actual.get("fees") or []
    fee_amounts = [str(f.get("amount")) for f in fees]
    checklist = actual.get("checklist") or []
    warnings = " ".join(actual.get("warnings") or []).lower()
    summary = (actual.get("summary") or "").lower()
    practical = actual.get("practical_notes") or []
    urls = actual.get("official_urls") or []
    citations = actual.get("citations") or []
    answer_blob = json.dumps(actual, ensure_ascii=False).lower()

    # Service match
    if expect.get("service_must_match") or case.get("service_expected"):
        expected = case.get("service_expected")
        if expected:
            ok = svc == expected
            if expect.get("allow_any_nid_family") and svc in NID_FAMILY:
                ok = True
            if expect.get("allow_bdris_family") and svc in BDRIS_FAMILY:
                ok = True
            if case.get("service_expected") is None and expect.get("allow_any_nid_family"):
                ok = svc in NID_FAMILY or svc is None
            checks["service"] = ok
            if not ok and expected:
                reasons.append(f"service mismatch: expected={expected} got={svc}")
        elif expect.get("allow_any_nid_family"):
            checks["service"] = svc in NID_FAMILY or svc is None
        elif expect.get("allow_bdris_family"):
            checks["service"] = svc in BDRIS_FAMILY or svc is None

    # Intent
    if case.get("intent_expected"):
        accept_list = list(expect.get("intent_accept") or [])
        accept_list.append(case["intent_expected"])
        secondary = (actual.get("entities") or {}).get("intent_secondary") or []
        ok = canonical_intent_matches(
            case["intent_expected"],
            intent or "",
            accept=set(accept_list),
            secondary=secondary,
        )
        if not ok and case["intent_expected"] in {"document_list", "procedure_inquiry", "general_info"}:
            if intent in {"document_list", "procedure_inquiry", "general_info"} and case.get("category") in {
                "vague",
                "abbreviation",
                "follow_up",
                "processing_time",
            }:
                ok = True
        checks["intent"] = ok
        if not ok:
            reasons.append(f"intent mismatch: expected={case['intent_expected']} got={intent}")

    # Seed checklist must not appear as official MUST NEED
    if expect.get("must_not_show_seed_checklist_as_official"):
        seedish = [
            c
            for c in checklist
            if not c.get("claim_linked") and c.get("type") in {"REQUIRED", "MUST"}
        ]
        ok = len(seedish) == 0
        checks["no_seed_must_need"] = ok
        if not ok:
            reasons.append(f"seed checklist leaked as official: {seedish}")

    # Practical labeling
    if expect.get("practical_must_be_labeled") or expect.get("practical_not_as_must_need"):
        practical_in_checklist = [
            c for c in checklist if "hospital" in (c.get("item") or "").lower() or "midwife" in (c.get("item") or "").lower()
        ]
        if expect.get("practical_not_as_must_need"):
            ok = len(practical_in_checklist) == 0
            checks["practical_not_must_need"] = ok
            if not ok:
                reasons.append("practical tip appeared in official checklist MUST NEED")
        if expect.get("practical_must_be_labeled") and practical:
            ok = all("[PRACTICAL" in p for p in practical)
            checks["practical_labeled"] = ok
            if not ok:
                reasons.append("practical notes missing PRACTICAL label")

    # Rejected / static NID amounts
    if expect.get("must_not_show_static_nid_amounts"):
        bad = [a for a in fee_amounts if a in {"230", "345", "460"}]
        ok = not bad and "230" not in summary
        checks["no_static_nid"] = ok
        if not ok:
            reasons.append(f"static NID fee amounts surfaced: {bad}")

    if expect.get("must_not_publish_rejected_500") or expect.get("must_not_affirm_rejected_fee"):
        affirmed = "500" in fee_amounts or (
            "500" in summary and "not confirmed" not in warnings and "not confirmed" not in summary
        )
        # Pass if 500 not in fees AND warning rejects or uncertainty
        ok = "500" not in fee_amounts
        if expect.get("must_reject_amount") == "500" or "500" in case["query"]:
            ok = ok and (
                "500" in warnings
                or "not confirmed" in warnings
                or "not yet verified" in warnings
                or "no verified official fee" in warnings
            )
        checks["reject_500"] = ok
        if not ok:
            reasons.append("rejected BDT 500 fee handling failed")

    # Explicit amount rejection
    if expect.get("must_reject_amount"):
        amt = str(expect["must_reject_amount"])
        ok = amt not in fee_amounts and (
            amt in warnings
            or "not confirmed" in warnings
            or "calculator" in warnings
            or "no verified official fee" in warnings
        )
        checks["reject_amount"] = ok
        if not ok:
            reasons.append(f"failed to reject unsupported amount {amt}")

    # Fee expectations
    if expect.get("fee_amount_expected"):
        ok = expect["fee_amount_expected"] in fee_amounts
        checks["fee_amount"] = ok
        if not ok:
            reasons.append(
                f"fee amount missing: expected {expect['fee_amount_expected']} in {fee_amounts}"
            )

    if expect.get("fee_amounts_any_of"):
        ok = any(a in fee_amounts for a in expect["fee_amounts_any_of"])
        checks["fee_any"] = ok
        if not ok:
            reasons.append(f"expected one of {expect['fee_amounts_any_of']} in fees {fee_amounts}")

    if expect.get("fee_mode_calculator"):
        ok = any(f.get("fee_mode") == "calculator" or f.get("amount") == "USE_OFFICIAL_CALCULATOR" for f in fees)
        ok = ok or "calculator" in warnings
        checks["calculator_fee"] = ok
        if not ok:
            reasons.append("calculator fee path not surfaced")

    # URL
    if expect.get("must_include_url"):
        needle = expect["must_include_url"].lower()
        ok = any(needle in u.lower() for u in urls) or any(
            needle in ((c.get("source_url") or "")).lower() for c in citations
        )
        checks["url"] = ok
        if not ok:
            reasons.append(f"missing official URL containing {needle}")

    if expect.get("must_not_affirm_fake_url"):
        ok = "fake-gov-bd-portal.example" not in " ".join(urls).lower()
        ok = ok and "fake-gov-bd-portal.example" not in " ".join(
            (c.get("source_url") or "") for c in citations
        ).lower()
        checks["no_fake_url"] = ok
        if not ok:
            reasons.append("affirmed fake government URL")

    if expect.get("must_not_invent_url") or expect.get("must_not_invent_address") or expect.get(
        "must_not_invent_sla"
    ) or expect.get("must_not_invent_procedure") or expect.get("must_not_invent_fee"):
        # Heuristic: inventing means asserting specifics without uncertainty when no verified data
        inventing = False
        if expect.get("must_not_invent_fee") and fee_amounts and not any(
            f.get("evidence_id") for f in fees
        ):
            inventing = True
        if expect.get("must_not_invent_sla") and re.search(r"\d+\s*(day|days|week|weeks)", summary):
            if "not" not in summary and "unverified" not in warnings:
                inventing = True
        if expect.get("must_not_invent_procedure") and len(actual.get("steps") or []) > 0:
            if not any(s.get("claim_linked") for s in (actual.get("steps") or [])):
                inventing = True
        checks["no_invention"] = not inventing
        if inventing:
            reasons.append("possible invention of unsupported facts")

    if expect.get("must_not_invent_conditional_must_need"):
        # Conditional MUST NEED must not appear without claim_linked CONDITIONAL items matching scenario
        invented = [
            c
            for c in checklist
            if c.get("type") in {"REQUIRED", "MUST"} and not c.get("claim_linked")
        ]
        ok = len(invented) == 0
        checks["no_invented_conditional"] = ok
        if not ok:
            reasons.append("invented conditional/MUST NEED requirements")

    # Citations
    if expect.get("citation_must_support"):
        ok = any(c.get("source_url") for c in citations) or any(urls)
        checks["citation"] = ok
        if not ok:
            reasons.append("citation missing supporting URL/evidence")

    # Decorative citation check (always soft)
    decorative = [
        c
        for c in citations
        if not c.get("source_url")
        and (c.get("excerpt") or "") == (actual.get("service_name") or "")
    ]
    if decorative and expect.get("citation_must_support"):
        reasons.append("decorative citations only")
        checks["citation"] = False

    # Clarification OK
    if expect.get("clarification_ok") and actual.get("clarifications_needed"):
        checks["clarification"] = True

    # Uncertainty appropriate
    if expect.get("uncertainty_ok") or expect.get("knowledge_gap_ok"):
        support = actual.get("support_level") or ""
        ok = (
            support in {"INSUFFICIENT_EVIDENCE", "PARTIALLY_SUPPORTED", "CONFLICTED"}
            or bool(actual.get("warnings"))
            or svc is None
        )
        checks["uncertainty"] = ok
        if not ok and support == "VERIFIED" and expect.get("knowledge_gap_ok"):
            reasons.append("claimed VERIFIED where knowledge gap expected")

    passed = len(reasons) == 0
    # If only soft checks and all true
    if checks and all(checks.values()) and not reasons:
        passed = True

    failure_class = None if passed else classify_failure(case, actual, reasons)
    return {
        "pass": passed,
        "checks": checks,
        "reasons": reasons,
        "failure_class": failure_class,
        "recommended_fix": _recommend(failure_class, reasons),
    }


def _recommend(failure_class: str | None, reasons: list[str]) -> str | None:
    if not failure_class:
        return None
    mapping = {
        "HALLUCINATION": "Strengthen unsupported-amount / fake-URL refusal in answer builder; never affirm unverified amounts.",
        "SEED_DATA_BUG": "Keep claim_id filter on checklist/fees/steps; never present seed rows as official MUST NEED.",
        "RETRIEVAL_BUG": "Improve service matching (Bangla aliases, phrase hints, published-claim boost).",
        "LANGUAGE_BUG": "Expand Banglish glossary and Bangla intent keywords.",
        "CITATION_BUG": "Cite ServiceLink / ClaimEvidence only; suppress decorative service-name citations.",
        "RULE_ENGINE_BUG": "Keep PRACTICAL claims in practical_notes; never merge into checklist REQUIRED.",
        "CLAIM_SELECTION_BUG": "Select only VERIFIED OFFICIAL fee claims; prefer calculator path for NID.",
        "KNOWLEDGE_GAP": "Do not invent; surface uncertainty until Batch research covers the gap.",
        "OTHER": "Inspect pipeline evidence and tighten expectation or fix matching stage.",
    }
    return mapping.get(failure_class, "Inspect pipeline.")


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
                k: v
                for k, v in ctx.entities.items()
                if k not in {"service", "agency"}
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
        judgment = evaluate_case(case, actual)
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


async def main() -> int:
    cases = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    session_factory = get_session_factory()
    results: list[dict[str, Any]] = []
    for case in cases:
        results.append(await run_one(session_factory, case))

    # Metrics
    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    failed = total - passed
    fail_classes = Counter(r["failure_class"] for r in results if not r["pass"])

    def accuracy(key_fn) -> float:
        scored = [key_fn(r) for r in results if key_fn(r) is not None]
        if not scored:
            return 0.0
        return round(100.0 * sum(1 for x in scored if x) / len(scored), 1)

    service_acc = accuracy(
        lambda r: (
            None
            if r["expected"]["service"] is None and not (r["expected"]["expect"] or {}).get("service_must_match")
            else r["checks"].get("service", r["actual"]["service_slug"] == r["expected"]["service"])
        )
    )
    # Recompute service accuracy properly
    svc_ok = 0
    svc_n = 0
    for r in results:
        exp = r["expected"]["service"]
        if exp is None and not (r["expected"]["expect"] or {}).get("allow_any_nid_family"):
            continue
        svc_n += 1
        got = r["actual"]["service_slug"]
        if exp and got == exp:
            svc_ok += 1
        elif (r["expected"]["expect"] or {}).get("allow_any_nid_family") and got in NID_FAMILY:
            svc_ok += 1
        elif (r["expected"]["expect"] or {}).get("allow_bdris_family") and got in BDRIS_FAMILY:
            svc_ok += 1
    service_acc = round(100.0 * svc_ok / svc_n, 1) if svc_n else 0.0

    intent_ok = sum(1 for r in results if r["checks"].get("intent", r["actual"]["intent"] == r["expected"]["intent"]))
    intent_n = sum(1 for r in results if r["expected"]["intent"])
    intent_acc = round(100.0 * intent_ok / intent_n, 1) if intent_n else 0.0

    hallu = fail_classes.get("HALLUCINATION", 0)
    citation_f = fail_classes.get("CITATION_BUG", 0)
    retrieval_f = fail_classes.get("RETRIEVAL_BUG", 0)
    rule_f = fail_classes.get("RULE_ENGINE_BUG", 0)
    seed_f = fail_classes.get("SEED_DATA_BUG", 0)
    kg = fail_classes.get("KNOWLEDGE_GAP", 0)

    # Unsupported claim / hallucination rates among hallucination-category tests
    hallu_cases = [r for r in results if r["category"] == "hallucination"]
    hallu_pass = sum(1 for r in hallu_cases if r["pass"])
    appropriate_uncertainty = sum(
        1
        for r in results
        if (r["expected"]["expect"] or {}).get("uncertainty_ok")
        and r["checks"].get("uncertainty", False)
    )
    uncertainty_n = sum(
        1 for r in results if (r["expected"]["expect"] or {}).get("uncertainty_ok")
    )

    bn_cases = [r for r in results if r["language"] == "bn"]
    banglish_cases = [r for r in results if r["language"] == "banglish"]
    bn_acc = round(100.0 * sum(1 for r in bn_cases if r["pass"]) / len(bn_cases), 1) if bn_cases else 0
    banglish_acc = (
        round(100.0 * sum(1 for r in banglish_cases if r["pass"]) / len(banglish_cases), 1)
        if banglish_cases
        else 0
    )

    unanswered = sum(1 for r in results if r["actual"]["service_slug"] is None)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch_id": "batch-01",
        "publication_mode": "local_dev_only",
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate_pct": round(100.0 * passed / total, 1),
        "hallucinations": hallu,
        "citation_failures": citation_f,
        "retrieval_failures": retrieval_f,
        "rule_failures": rule_f,
        "seed_data_issues": seed_f,
        "knowledge_gaps": kg,
        "failure_class_counts": dict(fail_classes),
        "metrics": {
            "service_identification_accuracy_pct": service_acc,
            "intent_accuracy_pct": intent_acc,
            "bangla_pass_pct": bn_acc,
            "banglish_pass_pct": banglish_acc,
            "hallucination_suite_pass_pct": round(100.0 * hallu_pass / len(hallu_cases), 1)
            if hallu_cases
            else None,
            "unsupported_claim_rate_pct": round(
                100.0 * hallu / max(1, len(hallu_cases)), 1
            ),
            "unanswered_rate_pct": round(100.0 * unanswered / total, 1),
            "appropriate_uncertainty_pct": round(
                100.0 * appropriate_uncertainty / max(1, uncertainty_n), 1
            ),
        },
        "highest_priority_fixes": [
            x
            for x, _ in sorted(fail_classes.items(), key=lambda kv: -kv[1])
        ][:5],
    }

    # Write artifacts
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

    write_markdown(summary, results, failures)
    print(json.dumps(summary, indent=2))
    return 0 if failed == 0 else 1


def write_markdown(summary: dict, results: list[dict], failures: list[dict]) -> None:
    lines: list[str] = []
    lines.append("# Batch 1 End-to-End Assistant Evaluation")
    lines.append("")
    lines.append(f"**Generated:** {summary['generated_at']}")
    lines.append("**Mode:** Local/development only — no deployment")
    lines.append("")
    lines.append("## Headline results")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|------:|")
    lines.append(f"| Total tests | {summary['total_tests']} |")
    lines.append(f"| Passed | {summary['passed']} |")
    lines.append(f"| Failed | {summary['failed']} |")
    lines.append(f"| Pass rate | {summary['pass_rate_pct']}% |")
    lines.append(f"| Hallucinations | {summary['hallucinations']} |")
    lines.append(f"| Citation failures | {summary['citation_failures']} |")
    lines.append(f"| Retrieval failures | {summary['retrieval_failures']} |")
    lines.append(f"| Rule failures | {summary['rule_failures']} |")
    lines.append(f"| Seed-data issues | {summary['seed_data_issues']} |")
    lines.append(f"| Knowledge gaps | {summary['knowledge_gaps']} |")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    for k, v in summary["metrics"].items():
        lines.append(f"- **{k}:** {v}")
    lines.append("")
    lines.append("## Failure classification")
    lines.append("")
    for k, v in summary["failure_class_counts"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("## Highest-priority fixes")
    lines.append("")
    for i, fix in enumerate(summary["highest_priority_fixes"], 1):
        lines.append(f"{i}. `{fix}`")
    lines.append("")
    lines.append("## Pipeline under test")
    lines.append("")
    lines.append(
        "USER QUERY → language → Banglish normalize → intent → service ID → "
        "entities → clarification → structured retrieval → claim-linked fees/"
        "checklist/steps → authority (support_level) → conflict → answer → "
        "citations → support level"
    )
    lines.append("")
    lines.append("## Fixes applied during evaluation (underlying causes)")
    lines.append("")
    lines.append("1. Banglish glossary: `jonmo`/`nibondhon` → birth/registration")
    lines.append("2. Bangla intent keywords for documents/fees/procedures")
    lines.append("3. Phrase/URL-aware service matching with published-claim boost")
    lines.append("4. Seed checklist/steps/fees without `claim_id` excluded from official MUST NEED")
    lines.append("5. PRACTICAL claims surfaced only in `practical_notes` with explicit label")
    lines.append("6. Citations prefer verified `ServiceLink` / claim evidence over decorative names")
    lines.append("7. Explicit refusal of unsupported fee amounts (230/345/460/500)")
    lines.append("8. Stale `CONFLICTED` service status no longer forced without conflicting claims")
    lines.append("")
    lines.append("## Sample failures")
    lines.append("")
    for r in failures[:15]:
        lines.append(f"### {r['id']} — `{r['failure_class']}`")
        lines.append(f"- Query: {r['query']}")
        lines.append(f"- Expected service: `{r['expected']['service']}` / got `{r['actual']['service_slug']}`")
        lines.append(f"- Reasons: {'; '.join(r['reasons'])}")
        lines.append(f"- Fix: {r['recommended_fix']}")
        lines.append("")
    lines.append("## Machine-readable artifacts")
    lines.append("")
    lines.append("- `data/evaluation/batch-01/queries.json`")
    lines.append("- `data/evaluation/batch-01/results.jsonl`")
    lines.append("- `data/evaluation/batch-01/summary.json`")
    lines.append("- `data/evaluation/batch-01/failures.json`")
    lines.append("")
    lines.append("## Stop condition")
    lines.append("")
    lines.append("Evaluation complete. No Batch 2. No deploy. MVP seeds not overwritten.")
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
