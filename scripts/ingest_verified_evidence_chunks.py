#!/usr/bin/env python3
"""Ingest verified published evidence into KnowledgeDocument/KnowledgeChunk (no embeddings)."""

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.application.knowledge.evidence_ingestion import EvidenceIngestionService
    from app.core.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        svc = EvidenceIngestionService(session, dry_run=args.dry_run)
        report = await svc.ingest_published_claims()
        if not args.dry_run:
            await session.commit()
        print(json.dumps({
            "documents_created": report.documents_created,
            "chunks_created": report.chunks_created,
            "skipped_practical": report.skipped_practical,
            "skipped_unverified": report.skipped_unverified,
            "skipped_existing": report.skipped_existing,
            "errors": report.errors,
        }, indent=2))

    await engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
