"""Feedback and source schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class FeedbackCreate(BaseModel):
    feedback_type: str = Field(..., min_length=1, max_length=64)
    comment: str | None = Field(default=None, max_length=2000)
    conversation_id: UUID | None = None
    message_id: UUID | None = None
    service_slug: str | None = None


class FeedbackResponse(ORMModel):
    id: UUID
    feedback_type: str
    comment: str | None = None
    created_at: datetime


class SourceOut(ORMModel):
    id: UUID
    domain: str
    title: str | None = None
    tier: int
    crawl_enabled: bool


class SourceVersionOut(ORMModel):
    id: UUID
    url: str
    fetched_at: datetime | None = None
    source_published_at: datetime | None = None
    source_updated_at: datetime | None = None
    is_published: bool


class SourceDetail(SourceOut):
    versions: list[SourceVersionOut] = Field(default_factory=list)
