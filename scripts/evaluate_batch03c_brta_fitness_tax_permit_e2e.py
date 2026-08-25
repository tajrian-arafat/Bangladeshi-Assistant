#!/usr/bin/env python3
"""Batch 3C BRTA fitness/tax/permit end-to-end evaluation (local/dev only)."""

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
from batch03c_eval_outcomes import BRTA_03C_FAMILY, evaluate_batch03c_outcome  # noqa: E402

OUT_DIR = REPO_ROOT / "data/evaluation/batch-03c-brta-fitness-tax-permit"
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

    if expect.get("allow_brta_03c_family") and svc in BRTA_03C_FAMILY:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if case.get("service_expected") and svc == case["service_expected"]:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if expect.get("clarification_ok") and not case.get("service_expected"):
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    outcome = evaluate_batch03c_outcome(case, actual, {"reasons": reasons, "checks": checks})
    failure_class = None if outcome["pass"] else _b01.classify_failure(case, actual, outcome["reasons"])
    citation_failures = sum(
        1 for r in outcome["reasons"] if "citation" in r.lower() or "official url" in r.lower()
    )
    return {
        "pass": outcome["pass"],
        "raw_pass": outcome["raw_pass"],
        "expected_outcome": outcome["expected_outcome"],
        "actual_outcome": outcome["actual_outcome"],
        "counts_as_product_failure": outcome["counts_as_product_failure"],
        "checks": outcome["checks"],
        "reasons": outcome["reasons"],
        "failure_class": failure_class,
        "citation_failures": citation_failures,
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


async def main() -> int:
    cases = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    session_factory = get_session_factory()
    results = [await run_one(session_factory, c) for c in cases]

    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    product_failures = [r for r in results if r.get("counts_as_product_failure")]
    hallucinations = sum(1 for r in product_failures if r.get("failure_class") == "HALLUCINATION")
    citation_failures = sum(r.get("citation_failures", 0) for r in results)
    outcome_counts = Counter(r["actual_outcome"] for r in results)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch_id": "batch-03c-brta-fitness-tax-permit",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_pct": round(100 * passed / total, 1) if total else 0,
        "hallucinations": hallucinations,
        "citation_failures": citation_failures,
        "outcome_counts": dict(outcome_counts),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "failures.json").write_text(
        json.dumps([r for r in results if not r["pass"]], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
