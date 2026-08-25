#!/usr/bin/env python3
"""Post-publication: detect legacy seed replacement candidates (no auto-approve)."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)


async def main() -> int:
    parser = argparse.ArgumentParser(description="Detect legacy seed replacement candidates")
    parser.add_argument("--batch", required=True, help="Batch slug e.g. batch-03a-brta-driving-licence")
    parser.add_argument("--record", action="store_true", help="Record PENDING replacement rows")
    parser.add_argument("--dry-run", action="store_true", help="No DB writes")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional report path under data/audit/",
    )
    args = parser.parse_args()

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.application.knowledge.seed_replacement import SeedReplacementService
    from app.core.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    dry_run = args.dry_run or not args.record

    async with session_factory() as session:
        svc = SeedReplacementService(session, repo_root=ROOT, dry_run=dry_run)
        report = await svc.discover_candidates(args.batch)
        recorded = 0
        if args.record and report.candidates:
            recorded = await svc.record_pending(report.candidates, args.batch)
        pending = await svc.count_pending_replacements(args.batch)

        payload = {
            "batch": args.batch,
            "candidates": len(report.candidates),
            "recorded_pending": recorded,
            "total_pending_for_batch": pending,
            "requires_human_approval": pending > 0,
            "candidate_details": [
                {
                    "claim_id": str(c.claim_id),
                    "service_slug": c.service_slug,
                    "research_claim_key": c.research_claim_key,
                    "replacement_kind": c.replacement_kind,
                    "existing_status": c.existing_status or "NEW",
                }
                for c in report.candidates
            ],
        }

        out_path = Path(args.output) if args.output else ROOT / "data" / "audit" / f"seed-candidates-{args.batch}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        if not dry_run:
            await session.commit()

        print(json.dumps({"ok": True, **payload, "output": str(out_path.relative_to(ROOT))}, indent=2))

    await engine.dispose()
    return 0 if not payload["requires_human_approval"] else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
