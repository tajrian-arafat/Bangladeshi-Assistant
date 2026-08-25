"""Conversation retrieval."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.domain.models.conversation import Conversation, Message


class ConversationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_conversation(self, conversation_id: UUID) -> Conversation:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise NotFoundError("Conversation", str(conversation_id))
        return conversation
