#!/usr/bin/env python3
"""Audit legacy/MVP seed rows and replacement candidates in the runtime database."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)


async def main() -> int:
    parser = argparse.ArgumentParser(description="Audit legacy seed inventory")
    parser.add_argument("--batch", default=None, help="Optional batch slug filter (e.g. batch-03a-brta-driving-licence)")
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "audit" / "legacy-seed-inventory.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.application.knowledge.seed_replacement import SeedReplacementService
    from app.core.config import get_settings
    from app.domain.models.seed_replacement import SeedReplacement
    from sqlalchemy import select

    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        svc = SeedReplacementService(session, repo_root=ROOT, dry_run=True)
        rows = await svc.audit_legacy_inventory(batch_id=args.batch)
        discover = await svc.discover_candidates(args.batch or "batch-01")

        replacement_rows = (
            await session.execute(select(SeedReplacement))
        ).scalars().all()

        by_status: dict[str, int] = {}
        for r in replacement_rows:
            by_status[r.status] = by_status.get(r.status, 0) + 1

        payload = {
            "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "batch_filter": args.batch,
            "summary": {
                "total_legacy_rows": len(rows),
                "legacy_with_verified_replacement": sum(1 for r in rows if r.verified_replacement_exists),
                "replacement_candidates": len(discover.candidates),
                "replacement_records_by_status": by_status,
                "services_affected": sorted({r.service_slug for r in rows}),
            },
            "legacy_rows": [
                {**asdict(r), "service_id": str(r.service_id)}
                for r in rows
            ],
            "replacement_candidates": [
                {
                    "claim_id": str(c.claim_id),
                    "service_slug": c.service_slug,
                    "catalogue_service_id": c.catalogue_service_id,
                    "research_claim_key": c.research_claim_key,
                    "replacement_kind": c.replacement_kind,
                    "existing_status": c.existing_status,
                    "verification_date": c.verification_date,
                    "replacement_reason": c.replacement_reason,
                    "before_snapshot": c.before_snapshot,
                    "after_snapshot": c.after_snapshot,
                }
                for c in discover.candidates
            ],
        }

        out = Path(args.output)
    if not out.is_absolute():
        out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "output": str(out.relative_to(ROOT)), "summary": payload["summary"]}, indent=2))

    await engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
