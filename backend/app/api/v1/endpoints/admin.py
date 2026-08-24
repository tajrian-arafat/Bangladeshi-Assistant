"""Admin API endpoints (RBAC to be added)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.application.services.admin_service import AdminService
from app.schemas.admin import (
    AdminDashboardStats,
    AdminReviewListResponse,
    FeatureFlagOut,
    FeatureFlagUpdate,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboardStats)
async def admin_dashboard(
    session: AsyncSession = Depends(get_session),
) -> AdminDashboardStats:
    return await AdminService(session).get_dashboard_stats()


@router.get("/feature-flags", response_model=list[FeatureFlagOut])
async def list_feature_flags(
    session: AsyncSession = Depends(get_session),
) -> list[FeatureFlagOut]:
    return await AdminService(session).list_feature_flags()


@router.patch("/feature-flags/{key}", response_model=FeatureFlagOut)
async def update_feature_flag(
    key: str,
    payload: FeatureFlagUpdate,
    session: AsyncSession = Depends(get_session),
) -> FeatureFlagOut:
    return await AdminService(session).update_feature_flag(key, payload.enabled)


@router.get("/review-queue", response_model=AdminReviewListResponse)
async def list_review_queue(
    session: AsyncSession = Depends(get_session),
) -> AdminReviewListResponse:
    return await AdminService(session).list_review_queue()
