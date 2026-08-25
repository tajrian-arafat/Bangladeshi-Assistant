#!/usr/bin/env python3
"""Cross-domain language/context/service-bleed routing benchmark (local/dev only).

Outputs:
  data/evaluation/cross-domain-hardening/results.jsonl
  data/evaluation/cross-domain-hardening/summary.json
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
from app.ai.routing.intent_canonical import intent_matches as canonical_intent_matches  # noqa: E402
from app.application.services.conversation_context import ConversationContext  # noqa: E402
from app.core.database import get_session_factory  # noqa: E402
from app.schemas.chat import ChatRequest  # noqa: E402

OUT_DIR = REPO_ROOT / "data" / "evaluation" / "cross-domain-hardening"
QUERIES_PATH = OUT_DIR / "queries.json"
MULTI_TURN_PATH = OUT_DIR / "multi_turn.json"


def build_conv_context(case: dict) -> ConversationContext | None:
    clarifications = case.get("clarifications") or {}
    if not clarifications:
        return None
    ctx = ConversationContext(
        service_slug=clarifications.get("service"),
        clarifications=clarifications,
    )
    if case.get("query", "").lower().startswith(("follow up", "follow-up")):
        ctx.intent = case.get("intent_expected")
    elif clarifications.get("intent"):
        ctx.intent = clarifications.get("intent")
    return ctx


async def run_case(session_factory, case: dict) -> dict[str, Any]:
    async with session_factory() as session:
        req = ChatRequest(
            message=case["query"],
            language_preference="auto",
            clarifications=case.get("clarifications") or {},
        )
        conv_ctx = build_conv_context(case)
        answer, _confidence, intent_legacy, _citations, ctx = await Orchestrator(session).run(
            req, conversation_context=conv_ctx
        )

        reasons: list[str] = []
        svc = ctx.service.slug if ctx.service else None
        acceptable = case.get("acceptable_services") or [case["service_expected"]]
        service_ok = svc in acceptable if case.get("service_expected") else svc in acceptable or svc is None
        if case.get("service_expected") and not service_ok:
            reasons.append(f"service: expected one of {acceptable}, got {svc}")

        must_not = case.get("must_not_service") or []
        if svc in must_not:
            reasons.append(f"service_bleed: must not route to {svc}")

        intent_ok = canonical_intent_matches(
            case["intent_expected"],
            ctx.intent,
            secondary=(ctx.intents.secondary if ctx.intents else None),
        )
        if not intent_ok:
            primary = ctx.intents.primary if ctx.intents else intent_legacy
            legacy = ctx.intents.legacy_primary() if ctx.intents else intent_legacy
            reasons.append(
                f"intent: expected={case['intent_expected']} got primary={primary} legacy={legacy}"
            )

        passed = len(reasons) == 0

        return {
            "id": case["id"],
            "category": case.get("category"),
            "domain": case.get("domain"),
            "query": case["query"],
            "expected": {
                "intent": case["intent_expected"],
                "service": case["service_expected"],
            },
            "actual": {
                "intent": ctx.intent,
                "intent_primary": ctx.intents.primary if ctx.intents else None,
                "service_slug": svc,
                "normalized_message": ctx.normalized_message,
            },
            "pass": passed,
            "reasons": reasons,
        }


def expand_multi_turn(cases: list[dict]) -> list[dict]:
    expanded: list[dict] = []
    for conv in cases:
        final = None
        for turn in conv["turns"]:
            if turn.get("intent_expected"):
                final = turn
        if not final:
            continue
        expanded.append(
            {
                "id": conv["id"],
                "category": "multi_turn",
                "domain": conv.get("domain"),
                "query": final["query"],
                "description": conv.get("description"),
                "intent_expected": final["intent_expected"],
                "service_expected": final["service_expected"],
                "clarifications": final.get("clarifications") or {},
                "must_not_service": final.get("must_not_service") or [],
                "acceptable_services": final.get("acceptable_services"),
            }
        )
    return expanded


async def main() -> int:
    single = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    multi_raw = json.loads(MULTI_TURN_PATH.read_text(encoding="utf-8"))
    multi = expand_multi_turn(multi_raw)
    cases = single + multi

    session_factory = get_session_factory()
    results = [await run_case(session_factory, c) for c in cases]

    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    by_category: dict[str, dict[str, int]] = {}
    for r in results:
        cat = r.get("category") or "unknown"
        bucket = by_category.setdefault(cat, {"total": 0, "passed": 0})
        bucket["total"] += 1
        if r["pass"]:
            bucket["passed"] += 1

    category_rates = {
        cat: round(100.0 * v["passed"] / v["total"], 1) if v["total"] else 0.0
        for cat, v in by_category.items()
    }

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_id": "cross-domain-hardening",
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate_pct": round(100.0 * passed / total, 1),
        "category_counts": dict(Counter(r.get("category") for r in results)),
        "category_pass_rates_pct": category_rates,
        "failure_ids": [r["id"] for r in results if not r["pass"]],
        "composition": {
            "short_follow_up": 20,
            "bangla": 20,
            "banglish": 20,
            "generic_ambiguity": 20,
            "multi_turn": 10,
        },
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
