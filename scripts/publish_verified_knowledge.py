#!/usr/bin/env python3
"""Publish gate CLI: sync research claims and/or publish VERIFIED knowledge.

Examples:
  python scripts/publish_verified_knowledge.py --batch batch-01 --dry-run
  python scripts/publish_verified_knowledge.py --batch batch-01 --sync-claims --dry-run
  python scripts/publish_verified_knowledge.py --batch batch-01 --publish --dry-run
  python scripts/publish_verified_knowledge.py --batch batch-01 --publish --commit

Never auto-marks claims VERIFIED without independent verification artifacts.
Requires: cd backend && alembic upgrade head
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from app.application.knowledge.publisher import KnowledgePublisher  # noqa: E402
from app.core.database import get_session_factory  # noqa: E402
from app.core.exceptions import ValidationError  # noqa: E402


async def run(args: argparse.Namespace) -> int:
    dry_run = True
    if (args.publish or args.sync_claims) and args.commit and not args.dry_run:
        dry_run = False
    if args.dry_run:
        dry_run = True

    do_sync = args.sync_claims or (not args.sync_only and not args.publish_only)
    do_publish = args.publish or (not args.sync_only and not args.publish_only)

    session_factory = get_session_factory()
    async with session_factory() as session:
        publisher = KnowledgePublisher(session, repo_root=REPO_ROOT, dry_run=dry_run)
        reports = []
        try:
            if do_sync:
                # Dry-run publication needs claims in DB for gate evaluation; rolled back after.
                sync_publisher = (
                    publisher
                    if not dry_run
                    else KnowledgePublisher(session, repo_root=REPO_ROOT, dry_run=False)
                )
                reports.append(await sync_publisher.sync_claims_from_staging(args.batch))
            if do_publish:
                reports.append(await publisher.publish_verified(args.batch))
        except ValidationError as exc:
            if dry_run:
                await session.rollback()
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
            return 1
        except Exception as exc:  # noqa: BLE001
            if dry_run:
                await session.rollback()
            msg = str(exc)
            if "no such table" in msg.lower() or "does not exist" in msg.lower():
                print(
                    json.dumps(
                        {
                            "ok": False,
                            "error": msg,
                            "hint": (
                                "Apply migrations first: "
                                "cd backend && alembic upgrade head "
                                "(revision 002_claims_publication)."
                            ),
                        },
                        indent=2,
                    )
                )
                return 2
            raise

        if dry_run:
            await session.rollback()
        else:
            await session.commit()

        out = []
        audit = {}
        for r in reports:
            entry = {
                "ok": r.ok,
                "dry_run": r.dry_run,
                "batch_id": r.batch_id,
                "synced_claims": r.synced_claims,
                "published_fees": r.published_fees,
                "published_checklist": r.published_checklist,
                "published_steps": r.published_steps,
                "published_urls": r.published_urls,
                "published_practical": r.published_practical,
                "skipped": r.skipped,
                "eligible_count": r.eligible_count,
                "rejected_by_gate_count": r.rejected_by_gate_count,
                "errors": r.errors,
                "actions_sample": r.actions[:30],
                "actions_total": len(r.actions),
            }
            if hasattr(r, "audit_summary"):
                audit = r.audit_summary()
                entry["audit"] = audit
            if r.post_readiness:
                entry["post_readiness"] = r.post_readiness
            if r.post_readiness_detail:
                entry["post_readiness_detail"] = r.post_readiness_detail
            out.append(entry)

        payload = {"ok": all(x["ok"] for x in out), "reports": out}
        if audit:
            payload["dry_run_audit"] = audit
        print(json.dumps(payload, indent=2))
        return 0 if all(x["ok"] for x in out) else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, help="Staging batch id (e.g. batch-01)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report without writing (default unless --commit)",
    )
    parser.add_argument(
        "--sync-claims",
        action="store_true",
        help="Upsert staging claims/evidence into DB (includes verification apply)",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Attempt to publish VERIFIED OFFICIAL claims into runtime fields",
    )
    parser.add_argument(
        "--sync-only",
        action="store_true",
        help="Only sync claims; do not publish",
    )
    parser.add_argument(
        "--publish-only",
        action="store_true",
        help="Only publish (assumes claims already synced)",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Actually write (required with --publish or --sync-claims to persist)",
    )
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
