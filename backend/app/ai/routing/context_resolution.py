"""Multi-turn context resolution for short follow-ups and clarifications."""

from __future__ import annotations

import re
from typing import Any

from app.ai.routing.intent_classifier import IntentResult
from app.application.services.conversation_context import ConversationContext


_FOLLOW_UP_INTENT_PATTERNS: dict[str, list[str]] = {
    "fee_inquiry": ["fee", "koto", "taka", "charge", "cost", "ফি", "টাকা"],
    "processing_time": ["koto din", "how long", "sla", "time", "din", "দিন", "কত"],
    "application_url": ["url", "portal", "website", "link", "online channel", "channel"],
    "office_locator": ["where", "kothay", "office", "location", "কোথায়", "কোথায়"],
    "document_list": ["document", "lagbe", "papers", "required", "কাগজ"],
    "procedure_inquiry": ["how", "kivabe", "procedure", "steps"],
    "eligibility": ["valid", "validity", "eligible", "qualify"],
    "general_info": ["eta", "this", "that", "same"],
}


def merge_clarifications(
    request_clarifications: dict[str, str] | None,
    conversation: ConversationContext | None,
) -> dict[str, str]:
    merged: dict[str, str] = {}
    if conversation:
        merged.update(conversation.clarifications)
    if request_clarifications:
        merged.update({k: v for k, v in request_clarifications.items() if v})
    return merged


def infer_channel_from_message(message: str) -> str | None:
    msg = message.lower()
    if any(w in msg for w in ("online channel", "online pcc", "online fee", "online clearance")):
        return "online"
    if "offline" in msg or "paper" in msg:
        return "offline"
    return None


def resolve_follow_up_intent(
    message: str,
    conversation: ConversationContext | None,
    current: IntentResult,
) -> IntentResult | None:
    """Inherit intent from conversation when the message is a short follow-up."""
    if not conversation or not conversation.intent:
        return None
    text = message.strip().lower()
    if len(text) > 64 and "follow up" not in text:
        return None

    for intent, tokens in _FOLLOW_UP_INTENT_PATTERNS.items():
        if any(re.search(rf"\b{re.escape(t)}\b", text) for t in tokens):
            if (
                conversation.service_slug == "police-clearance-certificate"
                and intent == "application_url"
                and any(w in text for w in ("channel", "online", "fee", "koto"))
            ):
                intent = "fee_inquiry"
            secondary = [s for s in current.secondary if s != intent]
            if conversation.intent not in {intent, *secondary}:
                secondary.insert(0, conversation.intent)
            return IntentResult(primary=intent, secondary=secondary[:3])

    if len(text.split()) <= 4:
        return IntentResult(
            primary=conversation.intent,
            secondary=[s for s in current.secondary if s != conversation.intent][:2],
        )
    return None


def apply_context_clarifications(
    message: str,
    clarifications: dict[str, str],
    conversation: ConversationContext | None,
) -> dict[str, str]:
    """Enrich clarifications from conversation state and follow-up phrasing."""
    result = dict(clarifications)
    if conversation:
        if conversation.service_slug and "service" not in result:
            result["service"] = conversation.service_slug
        channel = infer_channel_from_message(message)
        if channel:
            result["channel"] = channel
    if infer_channel_from_message(message) == "online" and "service" in result:
        if result["service"] == "police-clearance-certificate":
            result.setdefault("pcc_channel", "online")
    return result


def should_inherit_service(message: str, conversation: ConversationContext | None) -> bool:
    if not conversation or not conversation.service_slug:
        return False
    from app.application.services.conversation_context import ConversationContextService

    if not ConversationContextService.is_follow_up_message(message):
        return False
    text = message.strip().lower()
    if text.startswith("follow up") or text.startswith("follow-up"):
        return True
    if len(text.split()) <= 5:
        return True
    return False
