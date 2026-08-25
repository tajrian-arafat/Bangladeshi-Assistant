#!/usr/bin/env python3
"""Generic batch E2E evaluation — works for any batch with queries.json or auto-generated queries."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import sys
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

_b01_path = REPO_ROOT / "scripts/evaluate_batch01_e2e.py"
_spec = importlib.util.spec_from_file_location("evaluate_batch01_e2e", _b01_path)
_b01 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_b01)


def load_or_generate_queries(batch_slug: str, service_ids: list[str]) -> list[dict[str, Any]]:
    out_dir = REPO_ROOT / "data" / "evaluation" / batch_slug
    queries_path = out_dir / "queries.json"
    if queries_path.exists():
        doc = json.loads(queries_path.read_text(encoding="utf-8"))
        if isinstance(doc, list):
            return doc
        return list(doc.get("queries") or [])

    queries: list[dict[str, Any]] = []
    for sid in service_ids:
        queries.extend(
            [
                {
                    "id": f"{sid}-en-short",
                    "query": f"How do I apply for {sid.replace('-', ' ')}?",
                    "language": "en",
                    "service_expected": sid,
                    "category": "procedure",
                    "expect": {"service_must_match": True},
                },
                {
                    "id": f"{sid}-fee",
                    "query": f"What is the fee for {sid.replace('-', ' ')}?",
                    "language": "en",
                    "service_expected": sid,
                    "category": "fee",
                    "expect": {"allow_uncertainty": True},
                },
            ]
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    queries_path.write_text(json.dumps({"queries": queries}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return queries


async def run_one(session_factory, case: dict) -> dict[str, Any]:
    async with session_factory() as session:
        req = ChatRequest(
            message=case["query"],
            language_preference=case.get("language", "auto"),
            clarifications=case.get("clarifications") or {},
        )
        answer, confidence, intent, citations, ctx = await Orchestrator(session).run(req)
        actual = {
            "language": ctx.language,
            "intent": intent,
            "service_slug": ctx.service.slug if ctx.service else None,
            "summary": answer.summary,
            "fees": [f.model_dump() for f in answer.fees],
            "checklist": [c.model_dump() for c in answer.checklist],
            "official_urls": answer.official_urls,
            "warnings": answer.warnings,
            "practical_notes": answer.practical_notes,
            "citations": [c.model_dump() for c in citations],
        }
        evaluation = _b01.evaluate_case(case, actual)
        if case.get("expect", {}).get("allow_uncertainty") and not evaluation["pass"]:
            if any("knowledge gap" in r.lower() or "uncertain" in r.lower() for r in evaluation["reasons"]):
                evaluation["pass"] = True
                evaluation["expected_outcome"] = "CORRECT_UNCERTAINTY"
        return {"case": case, "actual": actual, "evaluation": evaluation}


async def main_async(batch_slug: str, service_ids: list[str]) -> int:
    out_dir = REPO_ROOT / "data" / "evaluation" / batch_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    queries = load_or_generate_queries(batch_slug, service_ids)
    session_factory = get_session_factory()
    results: list[dict[str, Any]] = []
    for case in queries:
        results.append(await run_one(session_factory, case))

    passed = sum(1 for r in results if r["evaluation"]["pass"])
    failed = len(results) - passed
    hallucinations = sum(
        1 for r in results if r["evaluation"].get("failure_class") == "HALLUCINATION"
    )
    citation_failures = sum(r["evaluation"].get("citation_failures", 0) for r in results)

    summary = {
        "batch": batch_slug,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "pass_pct": round(100.0 * passed / len(results), 2) if results else 0.0,
        "hallucinations": hallucinations,
        "citation_failures": citation_failures,
    }
    (out_dir / "results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n",
        encoding="utf-8",
    )
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    docs = REPO_ROOT / "docs" / "evaluation" / f"{batch_slug}-publication-e2e.md"
    docs.parent.mkdir(parents=True, exist_ok=True)
    docs.write_text(
        f"# {batch_slug} E2E\n\nPassed {passed}/{len(results)} ({summary['pass_pct']}%).\n",
        encoding="utf-8",
    )
    return 0 if hallucinations == 0 and citation_failures == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, help="Batch slug e.g. batch-04-tax-vat-customs")
    parser.add_argument("--service-ids", nargs="*", default=[], help="Optional service id list")
    args = parser.parse_args()

    service_ids = args.service_ids
    if not service_ids:
        queue_path = REPO_ROOT / ".automation" / "batch_queue.json"
        if queue_path.exists():
            queue = json.loads(queue_path.read_text(encoding="utf-8"))
            for b in queue.get("batches") or []:
                if b.get("slug") == args.batch:
                    service_ids = list(b.get("service_ids") or [])
                    break

    raise SystemExit(asyncio.run(main_async(args.batch, service_ids)))


if __name__ == "__main__":
    main()
