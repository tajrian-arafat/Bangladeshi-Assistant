"""Services catalog endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.application.services.service_catalog_service import ServiceCatalogService
from app.schemas.services import ServiceDetail, ServiceListResponse

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=ServiceListResponse)
async def list_services(
    category: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> ServiceListResponse:
    return await ServiceCatalogService(session).list_services(
        category=category, status=status, page=page, page_size=page_size
    )


@router.get("/{slug}", response_model=ServiceDetail)
async def get_service(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> ServiceDetail:
    return await ServiceCatalogService(session).get_service_by_slug(slug)
