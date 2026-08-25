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
    pending_claims: int = 0
    conflicting_claims: int = 0
    open_gaps: int = 0


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


class ClaimOut(ORMModel):
    id: UUID
    service_id: UUID
    research_claim_key: str | None = None
    claim_type: str
    subject: str
    predicate: str
    value: str
    information_class: str
    pipeline_status: str
    confidence: float | None = None
    verified_at: datetime | None = None
    is_published: bool
    review_notes: str | None = None
    created_at: datetime
    updated_at: datetime


class ClaimListResponse(BaseModel):
    items: list[ClaimOut]
    total: int


class ClaimActionRequest(BaseModel):
    notes: str | None = None
    force: bool = False
    admin_user_id: UUID | None = None


class ProvenanceResponse(BaseModel):
    claim_id: str
    pipeline_status: str
    information_class: str
    is_published: bool
    chain: list[dict] = Field(default_factory=list)


class KnowledgeGapOut(ORMModel):
    id: UUID
    service_id: UUID
    claim_id: UUID | None = None
    field_name: str | None = None
    gap_type: str
    priority: str
    description: str
    status: str
    created_at: datetime


class KnowledgeGapListResponse(BaseModel):
    items: list[KnowledgeGapOut]
    total: int
