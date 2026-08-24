"""Intent classification."""

from __future__ import annotations

import re
from typing import Any


def classify_intent(message: str, clarifications: dict[str, Any] | None = None) -> str:
    text = message.lower()
    # Fee (EN / Banglish / BN)
    if any(
        w in text
        for w in [
            "fee",
            "charge",
            "koto",
            "cost",
            "price",
            "calculator",
            "bdt",
            "taka",
            "how much",
            "ফি",
            "খরচ",
            "টাকা",
            "মূল্য",
            "ফ্রি",
            "free",
        ]
    ) or re.search(r"\b\d{2,4}\s*(bdt|taka|টাকা)?\b", text):
        # Numeric amount alone is weak — require fee context words nearby OR explicit currency
        if any(
            w in text
            for w in [
                "fee",
                "charge",
                "koto",
                "cost",
                "price",
                "bdt",
                "taka",
                "ফি",
                "খরচ",
                "টাকা",
                "ফ্রি",
                "free",
                "how much",
            ]
        ) or re.search(r"\b\d{2,4}\s*(bdt|taka)\b", text):
            return "fee_inquiry"
    # Office / location
    if any(
        w in text
        for w in [
            "where",
            "kothay",
            "office",
            "location",
            "address",
            "কোথায়",
            "কোথায়",
            "অফিস",
            "ঠিকানা",
        ]
    ):
        return "office_locator"
    # Eligibility
    if any(
        w in text
        for w in [
            "eligible",
            "eligibility",
            "joggo",
            "qualify",
            "যোগ্য",
            "কে করতে পারে",
        ]
    ):
        return "eligibility"
    # Procedure
    if any(
        w in text
        for w in [
            "how",
            "kivabe",
            "procedure",
            "step",
            "process",
            "korbo",
            "apply",
            "appointment",
            "কিভাবে",
            "কীভাবে",
            "প্রক্রিয়া",
            "প্রক্রিয়া",
            "পদ্ধতি",
            "ধাপ",
            "কী করতে হবে",
            "কি করতে হবে",
            "করতে হয়",
            "করতে হয়",
        ]
    ):
        return "procedure_inquiry"
    # Documents / requirements
    if any(
        w in text
        for w in [
            "document",
            "lagbe",
            "lage",
            "paper",
            "required",
            "ki ki",
            "কী কী",
            "কি কি",
            "কাগজ",
            "দলিল",
            "প্রয়োজন",
            "প্রয়োজন",
            "লাগে",
            "লাগবে",
        ]
    ):
        return "document_list"
    # Verification / URL
    if any(
        w in text
        for w in [
            "verify",
            "verification",
            "everify",
            "url",
            "website",
            "portal",
            "যাচাই",
            "লিংক",
        ]
    ):
        return "general_info"
    # Service keyword fallback → document_list
    if any(
        w in text
        for w in [
            "passport",
            "nid",
            "brta",
            "tin",
            "birth",
            "death",
            "জন্ম",
            "মৃত্যু",
            "এনআইডি",
            "ssc",
            "hsc",
            "marriage",
            "বিবাহ",
        ]
    ):
        return "document_list"
    return "general_info"
