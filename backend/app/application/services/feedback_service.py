"""User feedback service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.feedback import Feedback
from app.domain.models.knowledge import Service
from app.schemas.feedback import FeedbackCreate, FeedbackResponse


class FeedbackService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_feedback(
        self, payload: FeedbackCreate, *, user_id: UUID | None = None
    ) -> FeedbackResponse:
        service_id: UUID | None = None
        if payload.service_slug:
            result = await self.session.execute(
                select(Service.id).where(Service.slug == payload.service_slug)
            )
            service_id = result.scalar_one_or_none()

        feedback = Feedback(
            user_id=user_id,
            conversation_id=payload.conversation_id,
            message_id=payload.message_id,
            service_id=service_id,
            feedback_type=payload.feedback_type,
            comment=payload.comment,
        )
        self.session.add(feedback)
        await self.session.flush()
        return FeedbackResponse.model_validate(feedback)
