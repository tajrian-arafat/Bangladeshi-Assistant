"""Admin API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AdminDashboardStats(BaseModel):
    total_services: int
    active_services: int
    pending_reviews: int
    total_agencies: int
    total_districts: int


class FeatureFlagOut(ORMModel):
    id: UUID
    key: str
    enabled: bool
    description: str | None = None
    updated_at: datetime | None = None


class FeatureFlagUpdate(BaseModel):
    enabled: bool


class ReviewQueueItemOut(ORMModel):
    id: UUID
    status: str
    priority: int
    service_id: UUID | None = None
    notes: str | None = None
    created_at: datetime


class AdminReviewListResponse(BaseModel):
    items: list[ReviewQueueItemOut]
    total: int
