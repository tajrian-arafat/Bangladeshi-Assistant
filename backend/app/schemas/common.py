"""Common schema types."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    code: str
    message: str
    correlation_id: str
    details: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class ReadinessCheck(BaseModel):
    name: str
    status: str
    detail: str | None = None


class ReadinessResponse(BaseModel):
    status: str
    checks: list[ReadinessCheck]


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    pages: int


class TimestampMixin(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UUIDMixin(BaseModel):
    id: UUID
