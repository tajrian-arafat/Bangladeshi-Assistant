"""Chat API schemas."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: UUID | None = None
    language_preference: str = Field(default="auto", pattern="^(auto|bn|en)$")
    clarifications: dict[str, str] = Field(default_factory=dict)


class ChecklistItemResponse(BaseModel):
    item: str
    type: str
    evidence_id: str | None = None


class ProcedureStepResponse(BaseModel):
    order: int
    title: str
    official_url: str | None = None


class FeeResponse(BaseModel):
    amount: str
    currency: str
    evidence_id: str | None = None


class AnswerPayload(BaseModel):
    summary: str
    checklist: list[ChecklistItemResponse] = Field(default_factory=list)
    steps: list[ProcedureStepResponse] = Field(default_factory=list)
    fees: list[FeeResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    clarifications_needed: list[str] = Field(default_factory=list)


class CitationResponse(BaseModel):
    evidence_id: str | None = None
    source_title: str | None = None
    source_url: str | None = None
    tier: int | None = None
    last_verified_at: str | None = None
    excerpt: str | None = None


class ChatMetadata(BaseModel):
    intent: str
    service_slug: str | None = None
    processing_ms: int
    llm_used: bool
    fallback_mode: bool


class ChatResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    language: str
    confidence: str
    answer: AnswerPayload
    citations: list[CitationResponse] = Field(default_factory=list)
    metadata: ChatMetadata
