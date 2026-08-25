"""Agencies catalog endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.application.services.agency_service import AgencyService
from app.schemas.services import AgencyListResponse, AgencySummary

router = APIRouter(prefix="/agencies", tags=["agencies"])


@router.get("", response_model=AgencyListResponse)
async def list_agencies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> AgencyListResponse:
    return await AgencyService(session).list_agencies(page=page, page_size=page_size)


@router.get("/{slug}", response_model=AgencySummary)
async def get_agency(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> AgencySummary:
    return await AgencyService(session).get_agency_by_slug(slug)
