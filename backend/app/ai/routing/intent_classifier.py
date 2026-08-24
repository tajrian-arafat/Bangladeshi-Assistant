"""Expanded intent classification with multi-intent support."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.ai.routing.loader import load_capability_aliases, load_intent_taxonomy


@dataclass
class IntentResult:
    primary: str
    secondary: list[str] = field(default_factory=list)

    @property
    def all_intents(self) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for intent in [self.primary, *self.secondary]:
            if intent not in seen:
                seen.add(intent)
                ordered.append(intent)
        return ordered

    def legacy_primary(self) -> str:
        taxonomy = load_intent_taxonomy()
        entry = taxonomy.get("intents", {}).get(self.primary, {})
        return str(entry.get("legacy_alias") or self.primary)


def _text_has_any(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens if token)


def _collect_capability_hits(text: str) -> dict[str, bool]:
    aliases = load_capability_aliases()
    hits: dict[str, bool] = {}
    for group, cfg in aliases.get("capability_groups", {}).items():
        tokens: list[str] = []
        for key in ("synonyms_en", "synonyms_bn", "synonyms_banglish"):
            tokens.extend(cfg.get(key) or [])
        hits[group] = _text_has_any(text, [t.lower() for t in tokens])
    return hits


def classify_intents(message: str, clarifications: dict[str, Any] | None = None) -> IntentResult:
    """Classify primary and secondary intents from normalized or raw message."""
    text = message.lower()
    clarifications = clarifications or {}
    hits = _collect_capability_hits(text)
    scored: dict[str, float] = {}

    def bump(intent: str, weight: float) -> None:
        scored[intent] = scored.get(intent, 0.0) + weight

    # Fee inquiry — strong signal
    if hits.get("fee") or re.search(r"\b\d{2,5}\s*(bdt|taka|টাকা)?\b", text):
        if hits.get("fee") or re.search(r"\b\d{2,5}\s*(bdt|taka)\b", text):
            bump("fee_inquiry", 40)

    # Fee matrix patterns (passport pages/years)
    if re.search(r"\d+\s*page|\bpage\b", text) and any(
        w in text for w in ["year", "bochor", "express", "regular", "fee", "bdt", "taka", "koto"]
    ):
        bump("fee_inquiry", 35)

    # Payment (distinct from fee amount questions)
    if hits.get("payment") and any(
        w in text for w in ["kivabe", "how", "method", "gateway", "pay", "payment", "পেমেন্ট"]
    ):
        bump("payment", 35)

    # Application URL
    if any(
        w in text
        for w in [
            "url",
            "website",
            "portal",
            "online url",
            "apply online",
            "onboarding",
            "কোথায়",
            "কোথায়",
        ]
    ):
        bump("application_url", 35)

    # Status
    if hits.get("status") or any(w in text for w in ["status check", "tracking", "track", "kotodur"]):
        bump("status", 40)

    # Appointment
    if hits.get("appointment"):
        bump("appointment", 40)

    # Office / location
    if any(
        w in text
        for w in ["where", "kothay", "office", "location", "address", "কোথায়", "কোথায়", "অফিস", "ঠিকানা"]
    ):
        bump("office_locator", 35)

    # Eligibility
    if any(w in text for w in ["eligible", "eligibility", "joggo", "qualify", "যোগ্য", "কে করতে পারে"]):
        bump("eligibility", 35)

    # Lost / damaged
    if hits.get("lost"):
        bump("lost_document", 40)
    if any(w in text for w in ["হারালে", "হারিয়ে", "হারিয়ে", "harano", "hariye"]):
        bump("lost_document", 38)
    if any(w in text for w in ["damaged", "damage", "torn", "ছিঁড়ে", "নষ্ট"]):
        bump("damaged_document", 35)

    # Correction
    if hits.get("correction"):
        bump("correction", 35)

    # Reissue / renewal
    if hits.get("reissue"):
        if any(w in text for w in ["renew", "renewal", "reissue", "re-issue", "নবায়ন"]):
            bump("renewal", 30)
            bump("reissue", 25)

    # Application (new)
    if hits.get("application") or any(w in text for w in ["korte chai", "apply", "new passport", "new e-passport"]):
        bump("application", 30)
    if any(w in text for w in ["korte chai", "korbo", "korte hobe"]) and "status" not in text:
        bump("application", 20)
    if re.search(r"\bnew\b", text) and any(
        w in text for w in ["korte chai", "korbo", "passport", "e-passport", "e passport"]
    ):
        bump("application", 40)

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
        bump("document_list", 35)

    # Procedure / how-to
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
        bump("procedure_inquiry", 25)

    # Processing time
    if any(w in text for w in ["time", "days", "weeks", "koto din", "processing", "sla", "কত দিন"]):
        bump("processing_time", 25)

    # Comparison
    if any(w in text for w in ["difference", " vs ", "compare", "mrp naki", "naki e-passport"]):
        bump("comparison", 25)

    # Verification / URL
    if any(w in text for w in ["verify", "verification", "everify", "url", "website", "portal", "যাচাই", "লিংক"]):
        bump("procedure_inquiry", 15)
        bump("general_info", 10)

    # Mission / abroad context
    if hits.get("mission"):
        bump("renewal", 10)
        bump("procedure_inquiry", 10)

    # Police verification
    if hits.get("police_verification"):
        bump("procedure_inquiry", 25)
        bump("eligibility", 15)
        bump("processing_time", 20)

    # Clarification overrides
    if clarifications.get("passport_type") == "mrp":
        bump("comparison", 5)
    if clarifications.get("application_type") in {"renewal", "reissue"}:
        bump("renewal", 15)
        bump("reissue", 15)

    if not scored:
        # Domain keyword fallback
        if any(w in text for w in ["passport", "nid", "brta", "tin", "birth", "death", "জন্ম", "মৃত্যু", "এনআইডি"]):
            return IntentResult(primary="document_list")
        return IntentResult(primary="general_info")

    ranked = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)
    primary = ranked[0][0]
    secondary = [intent for intent, score in ranked[1:] if score >= ranked[0][1] * 0.6]
    return IntentResult(primary=primary, secondary=secondary)


def classify_intent(message: str, clarifications: dict[str, Any] | None = None) -> str:
    """Backward-compatible single-intent classifier returning legacy alias."""
    return classify_intents(message, clarifications).legacy_primary()
