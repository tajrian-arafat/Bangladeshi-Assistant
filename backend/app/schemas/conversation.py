"""Conversation schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import ORMModel


class MessageOut(ORMModel):
    id: UUID
    role: str
    content: str
    language: str | None = None
    confidence: str | None = None
    intent: str | None = None
    service_slug: str | None = None
    created_at: datetime


class ConversationOut(BaseModel):
    id: UUID
    messages: list[MessageOut]
