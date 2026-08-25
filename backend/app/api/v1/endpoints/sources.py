"""Source transparency endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.application.services.source_service import SourceService
from app.schemas.feedback import SourceDetail, SourceOut

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceOut])
async def list_sources(
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[SourceOut]:
    return await SourceService(session).list_sources(limit=limit)


@router.get("/{source_id}", response_model=SourceDetail)
async def get_source(
    source_id: str,
    session: AsyncSession = Depends(get_session),
) -> SourceDetail:
    return await SourceService(session).get_source(source_id)
