#!/usr/bin/env python3
"""Publish gate CLI: sync research claims and/or publish VERIFIED knowledge.

Examples:
  python scripts/publish_verified_knowledge.py --batch batch-01 --dry-run
  python scripts/publish_verified_knowledge.py --batch batch-01 --sync-claims --dry-run
  python scripts/publish_verified_knowledge.py --batch batch-01 --publish --dry-run
  python scripts/publish_verified_knowledge.py --batch batch-01 --publish --commit

Never auto-marks claims VERIFIED. Fails safely if validation fails.
Requires: cd backend && alembic upgrade head
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.application.knowledge.publisher import KnowledgePublisher  # noqa: E402
from app.core.database import session_scope  # noqa: E402
from app.core.exceptions import ValidationError  # noqa: E402


async def run(args: argparse.Namespace) -> int:
    dry_run = True
    if (args.publish or args.sync_claims) and args.commit and not args.dry_run:
        dry_run = False
    if args.dry_run:
        dry_run = True

    async with session_scope() as session:
        publisher = KnowledgePublisher(session, repo_root=REPO_ROOT, dry_run=dry_run)
        reports = []
        try:
            if args.sync_claims:
                reports.append(await publisher.sync_claims_from_staging(args.batch))
            if args.publish:
                reports.append(await publisher.publish_verified(args.batch))
            if not args.sync_claims and not args.publish:
                reports.append(await publisher.publish_verified(args.batch))
        except ValidationError as exc:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
            return 1
        except Exception as exc:  # noqa: BLE001
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

        out = []
        for r in reports:
            out.append(
                {
                    "ok": r.ok,
                    "dry_run": r.dry_run,
                    "batch_id": r.batch_id,
                    "synced_claims": r.synced_claims,
                    "published_fees": r.published_fees,
                    "published_checklist": r.published_checklist,
                    "published_steps": r.published_steps,
                    "skipped": r.skipped,
                    "errors": r.errors,
                    "actions_sample": r.actions[:30],
                    "actions_total": len(r.actions),
                }
            )
        print(json.dumps({"ok": all(x["ok"] for x in out), "reports": out}, indent=2))
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
        help="Upsert staging claims/evidence into DB without verifying/publishing",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Attempt to publish VERIFIED OFFICIAL claims into runtime fields",
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
