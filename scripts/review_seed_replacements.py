#!/usr/bin/env python3
"""Review and apply controlled MVP seed replacements."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review MVP seed replacement candidates",
        epilog=(
            "Workflow: --dry-run → --record → --approve <id> → --apply\n"
            "Bulk --approve-all is available but not recommended for high-risk replacements."
        ),
    )
    parser.add_argument("--batch", default="batch-01")
    parser.add_argument("--dry-run", action="store_true", help="Evaluate only; no DB writes")
    parser.add_argument("--record", action="store_true", help="Record PENDING replacement rows")
    parser.add_argument(
        "--approve",
        action="append",
        dest="approve_ids",
        default=[],
        help="Approve a specific replacement UUID (repeatable)",
    )
    parser.add_argument(
        "--approve-claim",
        action="append",
        dest="approve_claims",
        default=[],
        help="Approve by research_claim_key",
    )
    parser.add_argument(
        "--approve-all",
        action="store_true",
        help="Approve all PENDING replacements (use only for low-risk bulk after validation)",
    )
    parser.add_argument(
        "--reject",
        action="append",
        dest="reject_ids",
        default=[],
        help="Reject a specific replacement UUID",
    )
    parser.add_argument("--apply", action="store_true", help="Apply APPROVED replacements")
    parser.add_argument("--rollback", type=str, help="Rollback an APPLIED replacement by ID")
    args = parser.parse_args()

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.application.knowledge.seed_replacement import SeedReplacementService
    from app.core.config import get_settings

    settings = get_settings()
    db_url = settings.database_url
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    write_actions = args.record or args.approve_all or args.approve_ids or args.approve_claims
    write_actions = write_actions or args.reject_ids or args.apply or args.rollback
    dry_run = args.dry_run and not write_actions

    async with session_factory() as session:
        svc = SeedReplacementService(session, repo_root=ROOT, dry_run=dry_run)

        if args.rollback:
            ok = await svc.rollback(UUID(args.rollback))
            if not dry_run:
                await session.commit()
            print(json.dumps({"rolled_back": ok, "replacement_id": args.rollback}, indent=2))
            return 0 if ok else 1

        report = await svc.discover_candidates(args.batch)
        print("=== Seed replacement candidates ===")
        for c in report.candidates:
            print(
                f"  {c.research_claim_key} ({c.replacement_kind}) "
                f"service={c.service_slug} claim_id={c.claim_id} "
                f"status={c.existing_status or 'NEW'}"
            )
        print(f"Total candidates: {len(report.candidates)}")

        if args.record and report.candidates:
            n = await svc.record_pending(report.candidates, args.batch)
            print(f"Recorded {n} PENDING replacement(s)")

        if args.reject_ids:
            n = await svc.reject(
                replacement_ids=[UUID(rid) for rid in args.reject_ids],
                reason="Rejected via review_seed_replacements.py",
            )
            print(f"Rejected {n} replacement(s)")

        if args.approve_all or args.approve_claims or args.approve_ids:
            claim_ids = None
            replacement_ids = [UUID(rid) for rid in args.approve_ids] if args.approve_ids else None
            if args.approve_claims:
                from sqlalchemy import select

                from app.domain.models.claims import Claim

                keys = set(args.approve_claims)
                rows = (
                    await session.execute(
                        select(Claim.id).where(Claim.research_claim_key.in_(keys))
                    )
                ).scalars().all()
                claim_ids = list(rows)
            n = await svc.approve(
                claim_ids=claim_ids,
                replacement_ids=replacement_ids,
                approved_by="review_script",
            )
            print(f"Approved {n} replacement(s)")

        if args.apply:
            apply_report = await svc.apply_approved(args.batch)
            print(
                json.dumps(
                    {
                        "applied": apply_report.applied,
                        "skipped": apply_report.skipped,
                        "errors": apply_report.errors,
                    },
                    indent=2,
                )
            )

        if not dry_run:
            await session.commit()
        elif args.dry_run:
            print("\n[DRY RUN] No changes committed.")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
