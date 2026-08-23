"""Chat orchestration service (deterministic MVP stub)."""

import time
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain.models.conversation import Conversation, Message
from app.domain.models.knowledge import Service
from app.schemas.chat import (
    AnswerPayload,
    ChatMetadata,
    ChatRequest,
    ChatResponse,
    ChecklistItemResponse,
    FeeResponse,
    ProcedureStepResponse,
)


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        start = time.perf_counter()

        conversation = await self._get_or_create_conversation(request.conversation_id)
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            language=request.language_preference,
        )
        self.session.add(user_message)
        await self.session.flush()

        service = await self._match_service(request.message)
        answer, confidence, intent = await self._build_deterministic_answer(service, request)

        processing_ms = int((time.perf_counter() - start) * 1000)
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer.summary,
            language=request.language_preference,
            confidence=confidence,
            intent=intent,
            service_slug=service.slug if service else None,
            answer_json=answer.model_dump(),
            processing_ms=processing_ms,
            llm_used=False,
            fallback_mode=not self.settings.feature_llm_enabled,
        )
        self.session.add(assistant_message)
        await self.session.flush()

        return ChatResponse(
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            language=request.language_preference if request.language_preference != "auto" else "banglish",
            confidence=confidence,
            answer=answer,
            citations=[],
            metadata=ChatMetadata(
                intent=intent,
                service_slug=service.slug if service else None,
                processing_ms=processing_ms,
                llm_used=False,
                fallback_mode=not self.settings.feature_llm_enabled,
            ),
        )

    async def _get_or_create_conversation(self, conversation_id: UUID | None) -> Conversation:
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

    async def _match_service(self, message: str) -> Service | None:
        lowered = message.lower()
        result = await self.session.execute(select(Service))
        services = result.scalars().all()
        for service in services:
            if service.slug.replace("-", " ") in lowered:
                return service
            if service.name_en.lower() in lowered:
                return service
            aliases = service.aliases or []
            for alias in aliases:
                if alias.lower() in lowered:
                    return service
        return None

    async def _build_deterministic_answer(
        self, service: Service | None, request: ChatRequest
    ) -> tuple[AnswerPayload, str, str]:
        if not service:
            return (
                AnswerPayload(
                    summary=(
                        "I could not match your query to a known government service yet. "
                        "Please try browsing the service catalog or rephrase your question."
                    ),
                    clarifications_needed=["Which government service are you asking about?"],
                ),
                "low",
                "unsupported",
            )

        await self.session.refresh(service, ["checklist_items", "fees", "procedures"])
        for procedure in service.procedures:
            await self.session.refresh(procedure, ["steps"])

        checklist = [
            ChecklistItemResponse(
                item=item.label_en,
                type=item.item_type,
                evidence_id=str(item.evidence_chunk_id) if item.evidence_chunk_id else None,
            )
            for item in sorted(service.checklist_items, key=lambda x: x.order)
        ]
        steps: list[ProcedureStepResponse] = []
        for procedure in service.procedures:
            for step in sorted(procedure.steps, key=lambda x: x.order):
                steps.append(
                    ProcedureStepResponse(
                        order=step.order,
                        title=step.title_en,
                        official_url=step.official_url,
                    )
                )
        fees = [
            FeeResponse(
                amount=fee.amount,
                currency=fee.currency,
                evidence_id=str(fee.evidence_chunk_id) if fee.evidence_chunk_id else None,
            )
            for fee in service.fees
        ]

        confidence = "medium" if service.status == "ACTIVE" else "low"
        summary = (
            f"Here is structured guidance for {service.name_en}. "
            "Fees and URLs are shown only when verified in our knowledge base."
        )
        warnings: list[str] = []
        if service.status != "ACTIVE":
            warnings.append("This service is under review. Please verify details with the official office.")
        if not fees:
            warnings.append("Fee information is not yet verified. Confirm at the official office.")
        if not any(s.official_url for s in steps):
            warnings.append("Official application URLs are not yet verified.")

        return (
            AnswerPayload(
                summary=summary,
                checklist=checklist,
                steps=steps,
                fees=fees,
                warnings=warnings,
            ),
            confidence,
            "document_list" if checklist else "procedure_inquiry",
        )
