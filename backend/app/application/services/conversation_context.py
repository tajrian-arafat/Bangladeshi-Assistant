"""Conversation-scoped context for follow-up queries (no sensitive PII)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.conversation import ClarificationState, Conversation, Message


FOLLOW_UP_MAX_LEN = 48
FOLLOW_UP_TOKENS = {
    "naam",
    "name",
    "নাম",
    "dob",
    "date",
    "tarikh",
    "tarik",
    "জন্ম তারিখ",
    "other",
    "onno",
    "অন্য",
    "address",
    "ঠিকানা",
    "thikana",
    "yes",
    "no",
    "ha",
    "na",
    "হ্যাঁ",
    "না",
    "e-passport",
    "mrp",
    "renewal",
    "reissue",
    "motorcycle",
    "car",
}


@dataclass
class ConversationContext:
    service_slug: str | None = None
    intent: str | None = None
    entities: dict[str, Any] = field(default_factory=dict)
    clarifications: dict[str, str] = field(default_factory=dict)
    pending_clarifications: list[str] = field(default_factory=list)
    language: str | None = None

    def merge_clarifications(self, incoming: dict[str, str] | None) -> dict[str, str]:
        merged = dict(self.clarifications)
        if incoming:
            merged.update(incoming)
        return merged


class ConversationContextService:
    """Load/persist non-sensitive conversation context for follow-ups."""

    CONTEXT_KEYS = (
        "active_service_slug",
        "active_intent",
        "active_entities",
        "pending_clarifications",
        "active_language",
    )

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def load(self, conversation_id: UUID | None) -> ConversationContext:
        if not conversation_id:
            return ConversationContext()

        conv = await self.session.get(Conversation, conversation_id)
        if not conv:
            return ConversationContext()

        meta = conv.metadata_json or {}
        clarifications: dict[str, str] = {}
        result = await self.session.execute(
            select(ClarificationState).where(
                ClarificationState.conversation_id == conversation_id,
                ClarificationState.resolved.is_(True),
            )
        )
        for row in result.scalars().all():
            if row.value:
                clarifications[row.key] = row.value

        last_assistant = await self._last_assistant_message(conversation_id)
        if last_assistant:
            if last_assistant.service_slug and not meta.get("active_service_slug"):
                meta["active_service_slug"] = last_assistant.service_slug
            if last_assistant.intent and not meta.get("active_intent"):
                meta["active_intent"] = last_assistant.intent
            answer = last_assistant.answer_json or {}
            pending = answer.get("clarifications_needed") or []
            if pending and not meta.get("pending_clarifications"):
                meta["pending_clarifications"] = pending

        return ConversationContext(
            service_slug=meta.get("active_service_slug"),
            intent=meta.get("active_intent"),
            entities=meta.get("active_entities") or {},
            clarifications=clarifications,
            pending_clarifications=meta.get("pending_clarifications") or [],
            language=meta.get("active_language") or conv.language,
        )

    async def persist(
        self,
        conversation_id: UUID,
        *,
        service_slug: str | None,
        intent: str | None,
        entities: dict[str, Any],
        clarifications: dict[str, str],
        pending_clarifications: list[str],
        language: str | None,
        user_message: str,
    ) -> None:
        conv = await self.session.get(Conversation, conversation_id)
        if not conv:
            return

        safe_entities = {
            k: v
            for k, v in entities.items()
            if k in {"service_slug", "district", "location", "agency_slug"}
        }
        meta = dict(conv.metadata_json or {})
        if service_slug:
            meta["active_service_slug"] = service_slug
        if intent:
            meta["active_intent"] = intent
        if safe_entities:
            meta["active_entities"] = safe_entities
        if pending_clarifications:
            meta["pending_clarifications"] = pending_clarifications
        elif "pending_clarifications" in meta and not pending_clarifications:
            meta.pop("pending_clarifications", None)
        if language:
            meta["active_language"] = language
        conv.metadata_json = meta
        if language:
            conv.language = language

        for key, value in clarifications.items():
            if key.startswith("_"):
                continue
            existing = await self.session.execute(
                select(ClarificationState).where(
                    ClarificationState.conversation_id == conversation_id,
                    ClarificationState.key == key,
                )
            )
            row = existing.scalar_one_or_none()
            if row:
                row.value = value
                row.resolved = True
            else:
                self.session.add(
                    ClarificationState(
                        conversation_id=conversation_id,
                        key=key,
                        value=value,
                        resolved=True,
                    )
                )

        inferred = self._infer_clarification_from_follow_up(user_message, pending_clarifications)
        if inferred:
            key, value = inferred
            clarifications[key] = value
            existing = await self.session.execute(
                select(ClarificationState).where(
                    ClarificationState.conversation_id == conversation_id,
                    ClarificationState.key == key,
                )
            )
            row = existing.scalar_one_or_none()
            if row:
                row.value = value
                row.resolved = True
            else:
                self.session.add(
                    ClarificationState(
                        conversation_id=conversation_id,
                        key=key,
                        value=value,
                        resolved=True,
                    )
                )
            meta.pop("pending_clarifications", None)
            conv.metadata_json = meta

        await self.session.flush()

    async def _last_assistant_message(self, conversation_id: UUID) -> Message | None:
        result = await self.session.execute(
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.role == "assistant",
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def is_follow_up_message(message: str) -> bool:
        text = message.strip().lower()
        if not text:
            return False
        if len(text) <= FOLLOW_UP_MAX_LEN:
            tokens = set(text.replace(".", "").replace("?", "").split())
            if tokens & FOLLOW_UP_TOKENS:
                return True
            if len(text.split()) <= 3:
                return True
        return False

    @staticmethod
    def _infer_clarification_from_follow_up(
        message: str, pending: list[str]
    ) -> tuple[str, str] | None:
        if not pending:
            return None
        text = message.strip().lower()
        pending_text = " ".join(pending).lower()

        if any(
            k in pending_text
            for k in ("correction type", "correction do you need", "birth certificate correction", "সংশোধন")
        ):
            if text in {"naam", "name", "নাম"}:
                return ("correction_type", "name")
            if text in {"dob", "date", "tarikh", "tarik", "জন্ম তারিখ"}:
                return ("correction_type", "dob")
            if text in {"other", "onno", "অন্য", "address", "thikana", "ঠিকানা"}:
                return ("correction_type", "other")

        if "passport_type" in pending_text or "e-passport" in pending_text:
            if "e-passport" in text or "e passport" in text:
                return ("passport_type", "e-passport")
            if "mrp" in text:
                return ("passport_type", "mrp")

        if "application_type" in pending_text:
            if "renew" in text:
                return ("application_type", "renewal")
            if "reissue" in text:
                return ("application_type", "reissue")

        if "licence_class" in pending_text:
            if any(w in text for w in ("motorcycle", "bike", "motor")):
                return ("licence_class", "motorcycle")
            if "car" in text:
                return ("licence_class", "car")

        return None
