"""Source transparency queries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.domain.models.knowledge import Source
from app.schemas.feedback import SourceDetail, SourceOut, SourceVersionOut


class SourceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_source(self, source_id: str) -> SourceDetail:
        from uuid import UUID

        try:
            sid = UUID(source_id)
        except ValueError as exc:
            raise NotFoundError("Source", source_id) from exc

        result = await self.session.execute(
            select(Source)
            .where(Source.id == sid)
            .options(selectinload(Source.versions))
        )
        source = result.scalar_one_or_none()
        if not source:
            raise NotFoundError("Source", source_id)

        detail = SourceDetail.model_validate(source)
        detail.versions = [SourceVersionOut.model_validate(v) for v in source.versions]
        return detail

    async def list_sources(self, *, limit: int = 50) -> list[SourceOut]:
        result = await self.session.execute(select(Source).limit(limit))
        return [SourceOut.model_validate(s) for s in result.scalars().all()]
