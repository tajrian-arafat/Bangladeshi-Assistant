#!/usr/bin/env python3
"""Classify Batch 1 knowledge gaps for under-covered services."""

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

# Under-covered Batch 1 local attestation / registrar-list services
GAP_CLASSIFICATIONS = {
    "civil-marriage-registrar-hindu-list": {
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "critical_to_common_query": False,
        "description": "Hindu registrar list/search UI not independently confirmed on marriage.gov.bd.",
    },
    "civil-marriage-registrar-muslim-list": {
        "classification": "insufficient_evidence",
        "priority": "MEDIUM",
        "critical_to_common_query": False,
        "description": "Muslim registrar list/search UI not independently confirmed on marriage.gov.bd.",
    },
    "dc-attestation-photocopy": {
        "classification": "source_discovery_problem",
        "priority": "MEDIUM",
        "critical_to_common_query": False,
        "description": "LGI example URL not reachable; district attestation steps need official local source.",
    },
    "local-passport-attestation": {
        "classification": "geographic_local_variation",
        "priority": "MEDIUM",
        "critical_to_common_query": False,
        "description": "Union-level passport attestation varies by locality; no single national procedure page.",
    },
    "local-voter-transfer-attestation": {
        "classification": "geographic_local_variation",
        "priority": "MEDIUM",
        "critical_to_common_query": False,
        "description": "Union-level voter transfer attestation varies; needs district/union official source.",
    },
}


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.application.knowledge.publisher import KnowledgePublisher
    from app.core.config import get_settings
    from app.domain.enums import KnowledgeGapPriority, KnowledgeGapStatus, KnowledgeGapType
    from app.domain.models.claims import KnowledgeGap
    from app.domain.models.knowledge import Service

    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        publisher = KnowledgePublisher(session, repo_root=ROOT, dry_run=args.dry_run)
        mappings = await publisher.load_mappings()
        created = 0
        for catalogue_id, spec in GAP_CLASSIFICATIONS.items():
            service = await publisher.resolve_runtime_service(catalogue_id, mappings, None)
            if not service:
                print(f"SKIP {catalogue_id}: no runtime service")
                continue
            desc = spec["description"]
            existing = (
                await session.execute(
                    select(KnowledgeGap).where(
                        KnowledgeGap.service_id == service.id,
                        KnowledgeGap.description == desc,
                    ).limit(1)
                )
            ).scalar_one_or_none()
            if existing:
                print(f"EXISTS {catalogue_id}: {existing.gap_type}")
                continue
            gap_type = KnowledgeGapType.MISSING_EVIDENCE.value
            if spec["classification"] == "geographic_local_variation":
                gap_type = KnowledgeGapType.MISSING_LOCAL_RULE.value
            elif spec["classification"] == "source_discovery_problem":
                gap_type = KnowledgeGapType.MISSING_PROCEDURE.value
            if not args.dry_run:
                session.add(
                    KnowledgeGap(
                        service_id=service.id,
                        gap_type=gap_type,
                        priority=spec.get("priority", KnowledgeGapPriority.MEDIUM.value),
                        description=desc,
                        discovered_by="batch01_gap_classification",
                        status=KnowledgeGapStatus.OPEN.value,
                        resolution_notes=json.dumps(
                            {
                                "classification": spec["classification"],
                                "critical_to_common_query": spec["critical_to_common_query"],
                                "catalogue_service_id": catalogue_id,
                            },
                            ensure_ascii=False,
                        ),
                    )
                )
            created += 1
            print(f"{'WOULD CREATE' if args.dry_run else 'CREATED'} {catalogue_id}: {spec['classification']}")

        if not args.dry_run:
            await session.commit()
        print(f"\nTotal gaps {'would be ' if args.dry_run else ''}created: {created}")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
