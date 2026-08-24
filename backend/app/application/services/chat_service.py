"""Chat orchestration service."""

import json
import time
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm_client import LLMClient
from app.ai.orchestrator import Orchestrator
from app.application.services.conversation_context import ConversationContextService
from app.core.config import get_settings
from app.domain.models.conversation import Conversation, Message
from app.schemas.chat import ChatMetadata, ChatRequest, ChatResponse


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()
        self.orchestrator = Orchestrator(session)
        self.llm = LLMClient(self.settings)
        self.context_service = ConversationContextService(session)

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        start = time.perf_counter()

        conversation = await self._get_or_create_conversation(request.conversation_id)
        conversation_context = await self.context_service.load(conversation.id)
        merged_clarifications = conversation_context.merge_clarifications(request.clarifications)
        enriched_request = request.model_copy(update={"clarifications": merged_clarifications})

        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            language=request.language_preference,
        )
        self.session.add(user_message)
        await self.session.flush()

        answer, confidence, intent, citations, ctx = await self.orchestrator.run(
            enriched_request, conversation_context=conversation_context
        )

        llm_used = False
        if self.llm.enabled and not answer.clarifications_needed:
            evidence_json = json.dumps([c.model_dump() for c in citations], default=str)
            llm_summary = await self.llm.summarize(evidence_json, request.message, ctx.language)
            if llm_summary:
                answer.summary = llm_summary
                llm_used = True

        processing_ms = int((time.perf_counter() - start) * 1000)
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer.summary,
            language=ctx.language,
            confidence=confidence,
            intent=intent,
            service_slug=ctx.service.slug if ctx.service else None,
            answer_json=answer.model_dump(),
            processing_ms=processing_ms,
            llm_used=llm_used,
            fallback_mode=not llm_used,
        )
        self.session.add(assistant_message)
        await self.session.flush()

        await self.context_service.persist(
            conversation.id,
            service_slug=ctx.service.slug if ctx.service else conversation_context.service_slug,
            intent=intent,
            entities=ctx.entities,
            clarifications=merged_clarifications,
            pending_clarifications=answer.clarifications_needed,
            language=ctx.language,
            user_message=request.message,
        )

        return ChatResponse(
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            language=ctx.language if ctx.language != "auto" else "banglish",
            confidence=confidence,
            answer=answer,
            citations=citations,
            metadata=ChatMetadata(
                intent=intent,
                service_slug=ctx.service.slug if ctx.service else None,
                processing_ms=processing_ms,
                llm_used=llm_used,
                fallback_mode=not llm_used,
            ),
        )

    async def _get_or_create_conversation(self, conversation_id: UUID | None) -> Conversation:
        from sqlalchemy import select

        if conversation_id:
            result = await self.session.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation
        conversation = Conversation(id=conversation_id or uuid4())
        self.session.add(conversation)
        await self.session.flush()
        return conversation
