"""Admin operations service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.models.geography import District
from app.domain.models.knowledge import Agency, Service
from app.domain.models.operations import FeatureFlag, ReviewQueueItem
from app.schemas.admin import (
    AdminDashboardStats,
    AdminReviewListResponse,
    FeatureFlagOut,
    ReviewQueueItemOut,
)


class AdminService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_dashboard_stats(self) -> AdminDashboardStats:
        total_services = (
            await self.session.execute(select(func.count()).select_from(Service))
        ).scalar_one()
        active_services = (
            await self.session.execute(
                select(func.count()).select_from(Service).where(Service.status == "ACTIVE")
            )
        ).scalar_one()
        pending_reviews = (
            await self.session.execute(
                select(func.count())
                .select_from(ReviewQueueItem)
                .where(ReviewQueueItem.status == "pending")
            )
        ).scalar_one()
        total_agencies = (
            await self.session.execute(select(func.count()).select_from(Agency))
        ).scalar_one()
        total_districts = (
            await self.session.execute(select(func.count()).select_from(District))
        ).scalar_one()

        return AdminDashboardStats(
            total_services=total_services,
            active_services=active_services,
            pending_reviews=pending_reviews,
            total_agencies=total_agencies,
            total_districts=total_districts,
        )

    async def list_feature_flags(self) -> list[FeatureFlagOut]:
        result = await self.session.execute(select(FeatureFlag).order_by(FeatureFlag.key))
        return [FeatureFlagOut.model_validate(f) for f in result.scalars().all()]

    async def update_feature_flag(self, key: str, enabled: bool) -> FeatureFlagOut:
        result = await self.session.execute(select(FeatureFlag).where(FeatureFlag.key == key))
        flag = result.scalar_one_or_none()
        if not flag:
            raise NotFoundError("FeatureFlag", key)
        flag.enabled = enabled
        await self.session.flush()
        return FeatureFlagOut.model_validate(flag)

    async def list_review_queue(self, *, limit: int = 50) -> AdminReviewListResponse:
        result = await self.session.execute(
            select(ReviewQueueItem).order_by(ReviewQueueItem.priority.desc()).limit(limit)
        )
        items = [ReviewQueueItemOut.model_validate(i) for i in result.scalars().all()]
        total = (
            await self.session.execute(select(func.count()).select_from(ReviewQueueItem))
        ).scalar_one()
        return AdminReviewListResponse(items=items, total=total)
