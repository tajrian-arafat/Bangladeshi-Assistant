"""Hybrid search service (FTS stub with keyword matching)."""

import time

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.knowledge import KnowledgeChunk, Service
from app.schemas.search import SearchResponse, SearchResult


class SearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(self, query: str, *, limit: int = 20) -> SearchResponse:
        start = time.perf_counter()
        terms = query.lower().split()
        results: list[SearchResult] = []

        service_query = select(Service).where(Service.deleted_at.is_(None))
        service_filters = []
        for term in terms:
            pattern = f"%{term}%"
            service_filters.append(
                or_(
                    func.lower(Service.name_en).like(pattern),
                    func.lower(Service.name_bn).like(pattern),
                    func.lower(Service.slug).like(pattern),
                )
            )
        if service_filters:
            service_query = service_query.where(*service_filters)
        service_query = service_query.limit(limit)
        service_result = await self.session.execute(service_query)
        for service in service_result.scalars().all():
            results.append(
                SearchResult(
                    id=service.id,
                    result_type="service",
                    title=service.name_en,
                    excerpt=service.name_bn,
                    slug=service.slug,
                    score=0.8,
                    service_id=service.id,
                )
            )

        remaining = max(0, limit - len(results))
        if remaining > 0:
            chunk_query = select(KnowledgeChunk).limit(remaining)
            chunk_filters = []
            for term in terms:
                pattern = f"%{term}%"
                chunk_filters.append(func.lower(KnowledgeChunk.content).like(pattern))
            if chunk_filters:
                chunk_query = chunk_query.where(or_(*chunk_filters))
            chunk_result = await self.session.execute(chunk_query)
            for chunk in chunk_result.scalars().all():
                excerpt = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
                results.append(
                    SearchResult(
                        id=chunk.id,
                        result_type="knowledge_chunk",
                        title="Knowledge excerpt",
                        excerpt=excerpt,
                        score=0.5,
                        service_id=chunk.service_id,
                    )
                )

        processing_ms = int((time.perf_counter() - start) * 1000)
        return SearchResponse(
            query=query,
            results=results[:limit],
            total=len(results),
            processing_ms=processing_ms,
        )
