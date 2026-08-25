"""Service and agency catalog schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AgencySummary(ORMModel):
    id: UUID
    slug: str
    name_bn: str
    name_en: str
    acronym: str | None = None
    website_url: str | None = None


class ChecklistItemOut(ORMModel):
    id: UUID
    item_type: str
    label_bn: str
    label_en: str
    description_bn: str | None = None
    description_en: str | None = None
    order: int


class ProcedureStepOut(ORMModel):
    id: UUID
    order: int
    key: str
    title_bn: str
    title_en: str
    description_bn: str | None = None
    description_en: str | None = None
    official_url: str | None = None
    status: str


class FeeOut(ORMModel):
    id: UUID
    label_bn: str
    label_en: str
    amount: str
    currency: str
    effective_date: date | None = None


class ServiceSummary(ORMModel):
    id: UUID
    slug: str
    name_bn: str
    name_en: str
    category: str
    status: str
    agency_id: UUID


class ServiceDetail(ServiceSummary):
    aliases: list[str] | None = None
    eligibility: dict | None = None
    required_documents: list | None = None
    conditional_documents: list | None = None
    last_verified_at: datetime | None = None
    confidence: float | None = None
    review_state: str
    version: int
    checklist_items: list[ChecklistItemOut] = Field(default_factory=list)
    procedure_steps: list[ProcedureStepOut] = Field(default_factory=list)
    fees: list[FeeOut] = Field(default_factory=list)


class ServiceListResponse(BaseModel):
    items: list[ServiceSummary]
    total: int


class AgencyListResponse(BaseModel):
    items: list[AgencySummary]
    total: int
