"""Conversation endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.application.services.conversation_service import ConversationService
from app.schemas.conversation import ConversationOut, MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ConversationOut:
    conversation = await ConversationService(session).get_conversation(conversation_id)
    return ConversationOut(
        id=conversation.id,
        messages=[MessageOut.model_validate(m) for m in conversation.messages],
    )
