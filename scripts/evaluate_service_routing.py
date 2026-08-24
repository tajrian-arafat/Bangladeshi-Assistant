#!/usr/bin/env python3
"""Service routing regression benchmark (local/dev only).

Outputs:
  data/evaluation/service-routing/results.jsonl
  data/evaluation/service-routing/summary.json
"""

from __future__ import annotations

import asyncio
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
from app.ai.routing.claim_retrieval import ClaimRetrieval  # noqa: E402
from app.ai.routing.intent_canonical import intent_matches as canonical_intent_matches  # noqa: E402
from app.ai.routing.intent_classifier import IntentResult, classify_intents  # noqa: E402
from app.core.database import get_session_factory  # noqa: E402
from app.domain.models.claims import Claim  # noqa: E402
from app.schemas.chat import ChatRequest  # noqa: E402
from sqlalchemy import select  # noqa: E402

OUT_DIR = REPO_ROOT / "data" / "evaluation" / "service-routing"
QUERIES_PATH = OUT_DIR / "queries.json"
PREV_BATCH02_SUMMARY = REPO_ROOT / "data" / "evaluation" / "batch-02a-passport" / "summary.json"


def intent_matches(expected: str, actual_primary: str, actual_legacy: str) -> bool:
    return canonical_intent_matches(expected, actual_legacy) or canonical_intent_matches(
        expected, actual_primary
    )


async def run_case(session_factory, case: dict) -> dict[str, Any]:
    async with session_factory() as session:
        req = ChatRequest(message=case["query"], language_preference="auto")
        answer, confidence, intent_legacy, citations, ctx = await Orchestrator(session).run(req)
        intents = ctx.intents or IntentResult(primary=intent_legacy)
        claim_retrieval = ClaimRetrieval(session)

        reasons: list[str] = []
        svc = ctx.service.slug if ctx.service else None
        acceptable = case.get("acceptable_services") or [case["service_expected"]]
        service_ok = svc in acceptable if case.get("service_expected") else svc in acceptable or svc is None
        if case.get("service_expected") and not service_ok:
            reasons.append(f"service: expected one of {acceptable}, got {svc}")

        intent_ok = canonical_intent_matches(
            case["intent_expected"],
            ctx.intent,
            secondary=(ctx.intents.secondary if ctx.intents else None),
        )
        if not intent_ok:
            reasons.append(
                f"intent: expected={case['intent_expected']} "
                f"got primary={intents.primary} legacy={intents.legacy_primary()}"
            )

        claim_types: list[str] = []
        if ctx.service:
            claims = await claim_retrieval.published_claims(ctx.service.id, intents)
            claim_types = sorted({c.claim_type for c in claims})

        expected_claim_types = case.get("expected_claim_types") or []
        claim_ok = True
        knowledge_gap = False
        if expected_claim_types and ctx.service:
            claim_ok = any(ct in claim_types for ct in expected_claim_types)
            if not claim_ok:
                any_published = await session.execute(
                    select(Claim.id).where(
                        Claim.service_id == ctx.service.id,
                        Claim.is_published.is_(True),
                        Claim.claim_type.in_(expected_claim_types),
                    ).limit(1)
                )
                knowledge_gap = any_published.scalar_one_or_none() is None
                if not knowledge_gap and not ctx.clarifications_needed:
                    reasons.append(
                        f"claim_types: expected any of {expected_claim_types}, got {claim_types}"
                    )
                elif knowledge_gap:
                    claim_ok = True

        clarification_ok = bool(ctx.clarifications_needed) and case.get("expect_clarification")
        passed = len(reasons) == 0 or clarification_ok

        return {
            "id": case["id"],
            "query": case["query"],
            "domain": case.get("domain"),
            "expected": {
                "intent": case["intent_expected"],
                "service": case["service_expected"],
                "claim_types": expected_claim_types,
            },
            "actual": {
                "intent_primary": intents.primary,
                "intent_legacy": intents.legacy_primary(),
                "service_slug": svc,
                "claim_types_retrieved": claim_types,
                "knowledge_gap": knowledge_gap,
                "routing_candidates": ctx.entities.get("routing_candidates"),
                "clarifications_needed": ctx.clarifications_needed,
                "fee_count": len(answer.fees),
                "checklist_count": len(answer.checklist),
                "steps_count": len(answer.steps),
            },
            "pass": passed,
            "reasons": reasons,
        }


async def main() -> int:
    cases = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    session_factory = get_session_factory()
    results = [await run_case(session_factory, c) for c in cases]

    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    service_ok = sum(1 for r in results if not any("service:" in x for x in r["reasons"]))
    intent_ok = sum(1 for r in results if not any("intent:" in x for x in r["reasons"]))
    claim_ok = sum(1 for r in results if not any("claim_types:" in x for x in r["reasons"]))

    prev = {}
    if PREV_BATCH02_SUMMARY.exists():
        prev = json.loads(PREV_BATCH02_SUMMARY.read_text(encoding="utf-8"))

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate_pct": round(100.0 * passed / total, 1),
        "metrics": {
            "service_identification_pct": round(100.0 * service_ok / total, 1),
            "intent_identification_pct": round(100.0 * intent_ok / total, 1),
            "claim_retrieval_pct": round(100.0 * claim_ok / total, 1),
            "final_answer_pct": round(100.0 * passed / total, 1),
        },
        "previous_batch02_passport_e2e": {
            "pass_rate_pct": prev.get("pass_rate_pct"),
            "passed": prev.get("passed"),
            "failed": prev.get("failed"),
            "failure_class_counts": prev.get("failure_class_counts"),
        },
        "failure_ids": [r["id"] for r in results if not r["pass"]],
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "results.jsonl").open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
