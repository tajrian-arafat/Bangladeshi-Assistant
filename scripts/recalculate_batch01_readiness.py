#!/usr/bin/env python3
"""Recalculate Batch 1 service readiness from current runtime DB."""

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
    parser.add_argument("--batch", default="batch-01")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    from sqlalchemy import func, select
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.orm import selectinload

    from app.application.knowledge.publisher import KnowledgePublisher
    from app.core.config import get_settings
    from app.domain.enums import ClaimPipelineStatus, ClaimType, InformationClass
    from app.domain.models.claims import Claim, KnowledgeGap
    from app.domain.models.knowledge import ChecklistItem, Fee, KnowledgeChunk, ProcedureStep, Service, ServiceLink

    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        publisher = KnowledgePublisher(session, repo_root=ROOT, dry_run=True)
        mappings = await publisher.load_mappings()
        staging = publisher.staging_dir(args.batch)
        services_meta = json.loads((staging / "services.json").read_text(encoding="utf-8"))["services"]

        summary = {
            "published_official_claims": 0,
            "published_fees": 0,
            "published_checklist_items": 0,
            "published_procedure_steps": 0,
            "verified_urls": 0,
            "practical_claims": 0,
            "knowledge_chunks": 0,
            "open_gaps": 0,
            "services": {},
        }

        for meta in services_meta:
            cid = meta["service_id"]
            mapping = mappings.get(cid, {})
            service = await publisher.resolve_runtime_service(cid, mappings, None)
            if not service:
                continue
            claims = (
                await session.execute(
                    select(Claim).where(Claim.service_id == service.id)
                )
            ).scalars().all()
            published_official = [c for c in claims if c.is_published and c.information_class == InformationClass.OFFICIAL.value]
            verified = [c for c in claims if c.pipeline_status == ClaimPipelineStatus.VERIFIED.value and c.information_class == InformationClass.OFFICIAL.value]
            practical = [c for c in claims if c.information_class == InformationClass.PRACTICAL.value and c.is_published]
            fees = (await session.execute(select(Fee).where(Fee.service_id == service.id, Fee.claim_id.is_not(None)))).scalars().all()
            checklist = (await session.execute(select(ChecklistItem).where(ChecklistItem.service_id == service.id, ChecklistItem.claim_id.is_not(None)))).scalars().all()
            steps = (await session.execute(select(ProcedureStep).where(ProcedureStep.claim_id.is_not(None)))).scalars().all()
            links = (await session.execute(select(ServiceLink).where(ServiceLink.service_id == service.id))).scalars().all()
            chunks = (await session.execute(select(func.count()).select_from(KnowledgeChunk).where(KnowledgeChunk.service_id == service.id))).scalar() or 0
            gaps = (await session.execute(select(func.count()).select_from(KnowledgeGap).where(KnowledgeGap.service_id == service.id, KnowledgeGap.status == "OPEN"))).scalar() or 0

            critical_gaps = sum(1 for c in claims if c.pipeline_status == ClaimPipelineStatus.CONFLICTING.value and c.claim_type in {ClaimType.FEE.value, ClaimType.DOCUMENT.value})
            readiness = publisher._compute_readiness(claims=claims, published_official=len(published_official), critical_gaps=critical_gaps)

            summary["published_official_claims"] += len(published_official)
            summary["published_fees"] += len(fees)
            summary["published_checklist_items"] += len(checklist)
            summary["published_procedure_steps"] += len(steps)
            summary["verified_urls"] += len(links)
            summary["practical_claims"] += len(practical)
        total_chunks = (
            await session.execute(select(func.count()).select_from(KnowledgeChunk))
        ).scalar() or 0
        summary["knowledge_chunks"] = total_chunks
            summary["open_gaps"] += gaps
            summary["services"][cid] = {
                "runtime_slug": service.slug,
                "readiness": readiness,
                "verified_official_claims": len(verified),
                "published_official_claims": len(published_official),
                "published_fees": len(fees),
                "published_checklist": len(checklist),
                "published_steps": len(steps),
                "open_gaps": gaps,
                "knowledge_chunks": chunks,
            }

        out_path = args.output or ROOT / "data" / "evaluation" / "batch-01" / "readiness-recalc.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        print(f"\nWrote {out_path}")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
