"""Geography queries."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.domain.models.geography import District, Division
from app.schemas.geography import (
    DistrictListResponse,
    DistrictOut,
    DivisionListResponse,
    DivisionOut,
)


class GeographyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_divisions(self) -> DivisionListResponse:
        result = await self.session.execute(select(Division).order_by(Division.name_en))
        items = [DivisionOut.model_validate(d) for d in result.scalars().all()]
        return DivisionListResponse(items=items, total=len(items))

    async def list_districts(self, *, division_slug: str | None = None) -> DistrictListResponse:
        query = select(District).order_by(District.name_en)
        division_slug_out: str | None = None

        if division_slug:
            div_result = await self.session.execute(
                select(Division).where(Division.slug == division_slug)
            )
            division = div_result.scalar_one_or_none()
            if not division:
                raise NotFoundError("Division", division_slug)
            query = query.where(District.division_id == division.id)
            division_slug_out = division_slug

        result = await self.session.execute(query.options(selectinload(District.division)))
        items = [DistrictOut.model_validate(d) for d in result.scalars().all()]
        return DistrictListResponse(
            items=items, total=len(items), division_slug=division_slug_out
        )

    async def get_district_by_slug(self, slug: str) -> DistrictOut:
        result = await self.session.execute(select(District).where(District.slug == slug))
        district = result.scalar_one_or_none()
        if not district:
            raise NotFoundError("District", slug)
        return DistrictOut.model_validate(district)
