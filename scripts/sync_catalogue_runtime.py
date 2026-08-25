#!/usr/bin/env python3
"""Synchronize finalized catalogue CONFIRMED services into runtime Service rows.

Examples:
  python scripts/sync_catalogue_runtime.py --dry-run
  python scripts/sync_catalogue_runtime.py --apply

Does NOT verify claims, publish fees/requirements, or start Batch 2.
Idempotent. Requires: cd backend && alembic upgrade head
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
# Relative sqlite URL (./data/bda.db) is resolved from CWD — match alembic/runtime.
os.chdir(BACKEND_DIR)

from app.application.knowledge.catalogue_runtime_sync import CatalogueRuntimeSync  # noqa: E402
from app.core.database import session_scope  # noqa: E402
from app.core.exceptions import ValidationError  # noqa: E402


async def run(dry_run: bool) -> int:
    report_path = REPO_ROOT / "data" / "research" / "catalogue_runtime_sync_report.json"
    async with session_scope() as session:
        syncer = CatalogueRuntimeSync(session, repo_root=REPO_ROOT, dry_run=dry_run)
        try:
            report = await syncer.sync()
        except ValidationError as exc:
            payload = {"ok": False, "error": str(exc), "dry_run": dry_run}
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            return 1
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            payload = {"ok": False, "error": msg, "dry_run": dry_run}
            if "no such table" in msg.lower() or "does not exist" in msg.lower():
                payload["hint"] = (
                    "Apply migrations first: cd backend && alembic upgrade head "
                    "(through 003_catalogue_runtime_sync)."
                )
                print(json.dumps(payload, indent=2))
                return 2
            raise

        payload = report.to_dict()
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        report_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return 0 if report.ok else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Propose sync without writing")
    group.add_argument("--apply", action="store_true", help="Apply sync transactionally")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(dry_run=args.dry_run)))


if __name__ == "__main__":
    main()
