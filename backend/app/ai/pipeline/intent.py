"""Intent classification."""

from __future__ import annotations

from typing import Any


def classify_intent(message: str, clarifications: dict[str, Any] | None = None) -> str:
    text = message.lower()
    if any(w in text for w in ["fee", "charge", "koto", "cost", "price"]):
        return "fee_inquiry"
    if any(w in text for w in ["where", "kothay", "office", "location", "address"]):
        return "office_locator"
    if any(w in text for w in ["eligible", "eligibility", "joggo", "qualify"]):
        return "eligibility"
    if any(w in text for w in ["document", "lagbe", "paper", "required", "ki ki"]):
        return "document_list"
    if any(w in text for w in ["how", "kivabe", "procedure", "step", "process", "korbo"]):
        return "procedure_inquiry"
    if any(w in text for w in ["passport", "nid", "brta", "tin", "birth", "ssc", "hsc"]):
        return "document_list"
    return "general_info"
