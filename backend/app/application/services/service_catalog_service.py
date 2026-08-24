"""Service catalog queries."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.domain.models.knowledge import Procedure, Service
from app.schemas.services import ProcedureStepOut, ServiceDetail, ServiceListResponse, ServiceSummary


class ServiceCatalogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_services(
        self,
        *,
        category: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ServiceListResponse:
        query = select(Service).where(Service.deleted_at.is_(None))
        if category:
            query = query.where(Service.category == category)
        if status:
            query = query.where(Service.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        query = query.order_by(Service.name_en).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        items = [ServiceSummary.model_validate(s) for s in result.scalars().all()]
        return ServiceListResponse(items=items, total=total)

    async def get_service_by_slug(self, slug: str) -> ServiceDetail:
        query = (
            select(Service)
            .where(Service.slug == slug, Service.deleted_at.is_(None))
            .options(
                selectinload(Service.checklist_items),
                selectinload(Service.fees),
                selectinload(Service.procedures).selectinload(Procedure.steps),
            )
        )
        result = await self.session.execute(query)
        service = result.scalar_one_or_none()
        if not service:
            raise NotFoundError("Service", slug)

        procedure_steps = []
        for procedure in service.procedures:
            procedure_steps.extend(sorted(procedure.steps, key=lambda s: s.order))

        detail = ServiceDetail.model_validate(service)
        detail.procedure_steps = [ProcedureStepOut.model_validate(step) for step in procedure_steps]
        return detail
