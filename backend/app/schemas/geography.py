"""Geography API schemas."""

from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import ORMModel


class DivisionOut(ORMModel):
    id: UUID
    slug: str
    name_bn: str
    name_en: str


class DistrictOut(ORMModel):
    id: UUID
    slug: str
    name_bn: str
    name_en: str
    division_id: UUID
    bbs_code: str | None = None


class DistrictListResponse(BaseModel):
    items: list[DistrictOut]
    total: int
    division_slug: str | None = None


class DivisionListResponse(BaseModel):
    items: list[DivisionOut]
    total: int
