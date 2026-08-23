"""Agency catalog queries."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.models.knowledge import Agency
from app.schemas.services import AgencyListResponse, AgencySummary


class AgencyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_agencies(self, *, page: int = 1, page_size: int = 50) -> AgencyListResponse:
        query = select(Agency).where(Agency.deleted_at.is_(None), Agency.is_active.is_(True))
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()
        query = query.order_by(Agency.name_en).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        items = [AgencySummary.model_validate(a) for a in result.scalars().all()]
        return AgencyListResponse(items=items, total=total)

    async def get_agency_by_slug(self, slug: str) -> AgencySummary:
        result = await self.session.execute(
            select(Agency).where(Agency.slug == slug, Agency.deleted_at.is_(None))
        )
        agency = result.scalar_one_or_none()
        if not agency:
            raise NotFoundError("Agency", slug)
        return AgencySummary.model_validate(agency)
