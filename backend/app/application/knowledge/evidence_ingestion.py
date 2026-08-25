"""Ingest verified evidence into KnowledgeDocument/KnowledgeChunk (no embeddings)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import ClaimPipelineStatus, InformationClass
from app.domain.models.claims import Claim, ClaimEvidence
from app.domain.models.knowledge import KnowledgeChunk, KnowledgeDocument, Source, SourceVersion


@dataclass
class IngestionReport:
    dry_run: bool
    documents_created: int = 0
    chunks_created: int = 0
    skipped_practical: int = 0
    skipped_unverified: int = 0
    skipped_existing: int = 0
    actions: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


class EvidenceIngestionService:
    """Verified Evidence → KnowledgeDocument → KnowledgeChunk (RAG-ready, no vectors)."""

    def __init__(self, session: AsyncSession, *, dry_run: bool = True) -> None:
        self.session = session
        self.dry_run = dry_run

    async def ingest_published_claims(
        self, *, service_id: UUID | None = None
    ) -> IngestionReport:
        report = IngestionReport(dry_run=self.dry_run)
        stmt = (
            select(Claim)
            .where(Claim.is_published.is_(True))
            .options(selectinload(Claim.evidence_links))
        )
        if service_id:
            stmt = stmt.where(Claim.service_id == service_id)
        claims = (await self.session.execute(stmt)).scalars().all()

        for claim in claims:
            if claim.pipeline_status != ClaimPipelineStatus.VERIFIED.value:
                report.skipped_unverified += 1
                continue
            if claim.information_class == InformationClass.PRACTICAL.value:
                report.skipped_practical += 1
                report.actions.append(
                    {
                        "action": "skip_practical",
                        "claim_id": str(claim.id),
                        "reason": "PRACTICAL cannot become official knowledge chunk",
                    }
                )
                continue
            if claim.information_class != InformationClass.OFFICIAL.value:
                report.skipped_unverified += 1
                continue

            for ev in claim.evidence_links:
                if not ev.source_version_id:
                    continue
                chunk_key = f"claim:{claim.id}:sv:{ev.source_version_id}"
                existing_chunks = (
                    await self.session.execute(
                        select(KnowledgeChunk).where(KnowledgeChunk.service_id == claim.service_id)
                    )
                ).scalars().all()
                if any(
                    (c.metadata_json or {}).get("chunk_key") == chunk_key for c in existing_chunks
                ):
                    report.skipped_existing += 1
                    continue

                sv = await self.session.get(SourceVersion, ev.source_version_id)
                if not sv:
                    continue
                src = await self.session.get(Source, sv.source_id)
                tier = int(src.tier) if src else 6
                content = ev.evidence_excerpt or claim.value
                if not content or len(content.strip()) < 10:
                    continue

                doc = await self._get_or_create_document(sv, report)
                metadata = {
                    "chunk_key": chunk_key,
                    "source_version_id": str(sv.id),
                    "claim_id": str(claim.id),
                    "service_id": str(claim.service_id),
                    "information_class": claim.information_class,
                    "language": "bn",
                    "excerpt": ev.evidence_excerpt,
                    "locator": ev.locator,
                    "page_number": ev.page_number,
                    "section": ev.section,
                    "authority_tier": tier,
                    "last_verified_at": (
                        (ev.verified_at or claim.verified_at or datetime.now(timezone.utc)).isoformat()
                    ),
                    "research_claim_key": claim.research_claim_key,
                }
                if self.dry_run:
                    report.chunks_created += 1
                    report.actions.append(
                        {"action": "would_create_chunk", "claim_id": str(claim.id), **metadata}
                    )
                    continue

                chunk = KnowledgeChunk(
                    document_id=doc.id,
                    service_id=claim.service_id,
                    chunk_index=0,
                    content=content[:8000],
                    language="bn",
                    embedding=None,
                    metadata_json=metadata,
                )
                self.session.add(chunk)
                ev.knowledge_chunk_id = chunk.id
                report.chunks_created += 1
                report.actions.append(
                    {"action": "create_chunk", "claim_id": str(claim.id), "chunk_key": chunk_key}
                )

        if not self.dry_run:
            await self.session.flush()
        return report

    async def _get_or_create_document(
        self, sv: SourceVersion, report: IngestionReport
    ) -> KnowledgeDocument:
        existing = (
            await self.session.execute(
                select(KnowledgeDocument).where(KnowledgeDocument.source_version_id == sv.id)
            )
        ).scalar_one_or_none()
        if existing:
            return existing

        if self.dry_run:
            report.documents_created += 1
            doc = KnowledgeDocument(
                source_version_id=sv.id,
                title=sv.url,
                language="bn",
                content_text=None,
                status="published",
                untrusted_content=False,
                metadata_json={"ingested_from": "verified_evidence"},
            )
            self.session.add(doc)
            await self.session.flush()
            return doc

        doc = KnowledgeDocument(
            source_version_id=sv.id,
            title=sv.url,
            language="bn",
            content_text=None,
            status="published",
            untrusted_content=False,
            metadata_json={"ingested_from": "verified_evidence"},
        )
        self.session.add(doc)
        await self.session.flush()
        report.documents_created += 1
        return doc
