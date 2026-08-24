"""Hybrid retrieval service."""

from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.knowledge import KnowledgeChunk, Service


class HybridSearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        pattern = f"%{query[:80]}%"
        result = await self.session.execute(
            select(KnowledgeChunk)
            .where(KnowledgeChunk.content.ilike(pattern))
            .limit(limit)
        )
        chunks = result.scalars().all()
        if chunks:
            return [self._chunk_to_evidence(c) for c in chunks]
        return await self._fallback_service_search(query, limit)

    async def retrieve_for_service(self, service: Service, query: str) -> list[dict[str, Any]]:
        result = await self.session.execute(
            select(KnowledgeChunk).where(KnowledgeChunk.service_id == service.id).limit(10)
        )
        chunks = result.scalars().all()
        if chunks:
            return [self._chunk_to_evidence(c) for c in chunks]
        return [self._service_to_evidence(service)]

    async def _fallback_service_search(self, query: str, limit: int) -> list[dict[str, Any]]:
        pattern = f"%{query[:40]}%"
        result = await self.session.execute(
            select(Service).where(
                or_(Service.name_en.ilike(pattern), Service.name_bn.ilike(pattern), Service.slug.ilike(pattern))
            ).limit(limit)
        )
        return [self._service_to_evidence(s) for s in result.scalars().all()]

    def _chunk_to_evidence(self, chunk: KnowledgeChunk) -> dict[str, Any]:
        meta = chunk.metadata_json or {}
        return {
            "id": str(chunk.id),
            "source_title": meta.get("title", "Knowledge chunk"),
            "source_url": meta.get("source_url"),
            "tier": meta.get("tier", 6),
            "last_verified_at": meta.get("last_verified_at"),
            "excerpt": chunk.content[:500],
            "documents": meta.get("documents", []),
            "fee_amount": meta.get("fee_amount"),
        }

    def _service_to_evidence(self, service: Service) -> dict[str, Any]:
        return {
            "id": str(service.id),
            "source_title": service.name_en,
            "source_url": None,
            "tier": 2,
            "last_verified_at": service.last_verified_at,
            "excerpt": service.name_en,
        }
