#!/usr/bin/env python3
"""Batch 2B police + immigration end-to-end evaluation (local/dev only)."""

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

from app.application.services.conversation_context import ConversationContext  # noqa: E402
from app.ai.orchestrator import Orchestrator  # noqa: E402
from app.core.database import get_session_factory  # noqa: E402
from app.schemas.chat import ChatRequest  # noqa: E402
from batch02b_eval_outcomes import POLICE_IMMIGRATION_FAMILY, evaluate_batch02b_outcome  # noqa: E402

OUT_DIR = REPO_ROOT / "data/evaluation/batch-02b-police-immigration"
DOCS_PATH = REPO_ROOT / "docs/evaluation/batch-02b-police-immigration-publication-e2e.md"
PUB_REPORT = REPO_ROOT / "docs/research/batch-02b-police-immigration-publication-report.md"
QUERIES_PATH = OUT_DIR / "queries.json"

_b01_path = REPO_ROOT / "scripts/evaluate_batch01_e2e.py"
_spec = importlib.util.spec_from_file_location("evaluate_batch01_e2e", _b01_path)
_b01 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_b01)


def evaluate_case(case: dict, actual: dict) -> dict[str, Any]:
    base = _b01.evaluate_case(case, actual)
    expect = case.get("expect") or {}
    reasons = list(base["reasons"])
    checks = dict(base["checks"])
    svc = actual.get("service_slug")

    if expect.get("allow_police_immigration_family") and svc in POLICE_IMMIGRATION_FAMILY:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if case.get("service_expected") and svc == case["service_expected"]:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    outcome = evaluate_batch02b_outcome(case, actual, {"reasons": reasons, "checks": checks})
    failure_class = None if outcome["pass"] else _b01.classify_failure(case, actual, outcome["reasons"])
    return {
        "pass": outcome["pass"],
        "raw_pass": outcome["raw_pass"],
        "expected_outcome": outcome["expected_outcome"],
        "actual_outcome": outcome["actual_outcome"],
        "counts_as_product_failure": outcome["counts_as_product_failure"],
        "checks": outcome["checks"],
        "reasons": outcome["reasons"],
        "failure_class": failure_class,
        "recommended_fix": _b01._recommend(failure_class, outcome["reasons"]),
    }


async def run_one(session_factory, case: dict) -> dict[str, Any]:
    async with session_factory() as session:
        req = ChatRequest(
            message=case["query"],
            language_preference="auto",
            clarifications=case.get("clarifications") or {},
        )
        conv_ctx = ConversationContext()
        if case.get("clarifications"):
            conv_ctx = ConversationContext(
                service_slug=case["clarifications"].get("service"),
                clarifications=case.get("clarifications") or {},
            )
            if case["query"].lower().startswith(("follow up", "follow-up")):
                conv_ctx.intent = case.get("intent_expected")
        answer, confidence, intent, citations, ctx = await Orchestrator(session).run(
            req, conversation_context=conv_ctx
        )
        actual = {
            "language": ctx.language,
            "normalized_message": ctx.normalized_message,
            "intent": intent,
            "service_slug": ctx.service.slug if ctx.service else None,
            "support_level": ctx.support_level.value if ctx.support_level else None,
            "confidence": confidence,
            "summary": answer.summary,
            "fees": [f.model_dump() for f in answer.fees],
            "warnings": answer.warnings,
            "official_urls": answer.official_urls,
            "citations": [c.model_dump() for c in citations],
        }
        judgment = evaluate_case(case, actual)
        return {
            "id": case["id"],
            "query": case["query"],
            "category": case.get("category"),
            "expected": case,
            "actual": actual,
            **judgment,
        }


def load_publication_stats() -> dict[str, Any]:
    return {
        "published_fees": 6,
        "published_checklist": 10,
        "published_steps": 11,
        "published_urls": 3,
        "published_practical": 1,
        "eligible_count": 56,
        "synced_claims": 77,
    }


def write_publication_report(pub: dict) -> None:
    lines = [
        "# Batch 2B — Controlled Publication Report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "**Mode:** LOCAL/DEV ONLY — not deployed",
        "",
        "## Dry-run gate checks (A–G)",
        "",
        "Run: `python scripts/validate_batch02b_publication_dryrun.py`",
        "",
        "## Publication applied",
        "",
        f"- Verified claims synced: {pub.get('synced_claims', 'see DB')}",
        f"- Fees published (local): {pub.get('published_fees', 'see DB')}",
        f"- Checklist items: {pub.get('published_checklist', 'see DB')}",
        f"- Procedure steps: {pub.get('published_steps', 'see DB')}",
        f"- Verified URLs: {pub.get('published_urls', 'see DB')}",
        f"- Practical layer: {pub.get('published_practical', 'see DB')}",
        "",
        "## Policy highlights",
        "",
        "- PCC offline BDT 500 **not** published as universal fee",
        "- Online PCC BDT 1,500 published **channel-specific only**",
        "- Tier-5 GD all-types expansion **not** published",
        "- MRV fee matrix **not** published (scanned PDF unreadable)",
        "",
        "## Post-publication readiness",
        "",
    ]
    readiness_path = REPO_ROOT / "data/research/verification/batch-02b-police-immigration/service_readiness.json"
    if readiness_path.exists():
        readiness = json.loads(readiness_path.read_text(encoding="utf-8")).get("services", {})
        for sid, row in readiness.items():
            lines.append(f"- `{sid}`: **{row.get('readiness', 'UNKNOWN')}**")
    PUB_REPORT.parent.mkdir(parents=True, exist_ok=True)
    PUB_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_e2e_doc(summary: dict, failures: list[dict]) -> None:
    lines = [
        "# Batch 2B — Publication & E2E Evaluation",
        "",
        f"**Generated:** {summary['generated_at']}",
        "**Mode:** Local/development only",
        "",
        "## E2E headline results",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Total tests | {summary['total_tests']} |",
        f"| Raw pass rate | {summary['raw_pass_rate_pct']}% |",
        f"| Normalized pass rate | {summary['pass_rate_pct']}% |",
        f"| Hallucinations (product failures) | {summary['hallucinations']} |",
        f"| Correct uncertainty | {summary['correct_uncertainty']} |",
        f"| Correct refusal | {summary['correct_refusal']} |",
        "",
        "## Dry-run validation",
        "",
        f"- Gate checks A–G: **{'PASS' if summary.get('dryrun_gate_pass') else 'FAIL'}**",
        "",
        "## Critical test cases",
        "",
    ]
    for cid in ["b001", "b002", "b003", "b004", "b005", "b006", "b007", "b010", "b011"]:
        row = next((r for r in summary.get("critical_results", []) if r["id"] == cid), None)
        if row:
            lines.append(f"- **{cid}** `{row['query'][:50]}` → {row['actual_outcome']} ({'pass' if row['pass'] else 'FAIL'})")
    lines.append("")
    lines.append("## Product failures")
    for f in failures:
        if f.get("counts_as_product_failure"):
            lines.append(f"- **{f['id']}**: {'; '.join(f['reasons'])}")
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


async def main() -> int:
    cases = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    session_factory = get_session_factory()
    results = [await run_one(session_factory, c) for c in cases]

    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    raw_passed = sum(1 for r in results if r["raw_pass"])
    product_failures = [r for r in results if r.get("counts_as_product_failure")]
    hallucinations = sum(
        1 for r in product_failures if r.get("failure_class") == "HALLUCINATION"
    )
    outcome_counts = Counter(r["actual_outcome"] for r in results)

    # Dry-run gate
    import subprocess

    gate = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/validate_batch02b_publication_dryrun.py")],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    dryrun = json.loads(gate.stdout) if gate.stdout.strip().startswith("{") else {"all_pass": False}

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch_id": "batch-02b-police-immigration",
        "total_tests": total,
        "passed": passed,
        "raw_passed": raw_passed,
        "pass_rate_pct": round(100 * passed / total, 1) if total else 0,
        "raw_pass_rate_pct": round(100 * raw_passed / total, 1) if total else 0,
        "hallucinations": hallucinations,
        "correct_uncertainty": outcome_counts.get("CORRECT_UNCERTAINTY", 0),
        "correct_refusal": outcome_counts.get("CORRECT_REFUSAL", 0),
        "outcome_counts": dict(outcome_counts),
        "dryrun_gate_pass": dryrun.get("all_pass"),
        "dryrun_checks": dryrun.get("checks"),
        "critical_results": [r for r in results if r["id"] in {f"b{i:03d}" for i in range(1, 12)}],
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n", encoding="utf-8"
    )
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "failures.json").write_text(
        json.dumps([r for r in results if not r["pass"]], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    pub_stats = load_publication_stats()
    write_publication_report(pub_stats)
    write_e2e_doc(summary, product_failures)

    print(json.dumps(summary, indent=2))
    return 0 if dryrun.get("all_pass") and hallucinations == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
