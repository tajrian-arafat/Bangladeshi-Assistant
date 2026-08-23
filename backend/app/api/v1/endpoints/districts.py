"""Geography endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.application.services.geography_service import GeographyService
from app.schemas.geography import DistrictListResponse, DistrictOut, DivisionListResponse

router = APIRouter(prefix="/districts", tags=["geography"])


@router.get("", response_model=DistrictListResponse)
async def list_districts(
    division: str | None = Query(default=None, description="Filter by division slug"),
    session: AsyncSession = Depends(get_session),
) -> DistrictListResponse:
    return await GeographyService(session).list_districts(division_slug=division)


@router.get("/{slug}", response_model=DistrictOut)
async def get_district(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> DistrictOut:
    return await GeographyService(session).get_district_by_slug(slug)


divisions_router = APIRouter(prefix="/divisions", tags=["geography"])


@divisions_router.get("", response_model=DivisionListResponse)
async def list_divisions(
    session: AsyncSession = Depends(get_session),
) -> DivisionListResponse:
    return await GeographyService(session).list_divisions()
