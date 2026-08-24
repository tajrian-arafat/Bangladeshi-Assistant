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

    has_document_signal = any(
        w in text
        for w in [
            "document",
            "lagbe",
            "lage",
            "paper",
            "required",
            "what",
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
    )
    has_procedure_signal = any(
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
            "verify",
            "verification",
            "everify",
        ]
    )

    # Fee inquiry — strong signal
    if hits.get("fee") or re.search(r"\b(free|ফ্রি)\b", text):
        bump("fee_inquiry", 40)
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
        w in text for w in ["kivabe", "how", "method", "gateway", "pay", "payment", "পেমেন্ট", "online"]
    ):
        bump("payment", 35)
        if "fee" in text or "passport fee" in text:
            bump("procedure_inquiry", 20)

    # Application URL — prefer general_info for list/download URL availability questions
    url_list_query = any(w in text for w in ["list", "download"]) and any(
        w in text for w in ["url", "official", "website", "portal"]
    )
    if url_list_query and not any(w in text for w in ["apply", "application", "register", "onboarding"]):
        bump("general_info", 35)
    elif any(
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
        for w in ["where", "kothay", "office", "location", "কোথায়", "কোথায়", "অফিস", "ঠিকানা"]
    ):
        bump("office_locator", 35)
    elif "address" in text and not any(
        w in text for w in ["eligible", "eligibility", "only for", "who can", "can i"]
    ):
        bump("office_locator", 20)

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
            "ke pare",
            "ke korte pare",
            "korte pare",
            "who can",
            "can i get",
        ]
    ):
        bump("eligibility", 45)

    # Lost / damaged — procedure beats document when how-to is present
    if hits.get("lost"):
        if has_procedure_signal:
            bump("procedure_inquiry", 42)
            bump("lost_document", 30)
        else:
            bump("lost_document", 40)
    if any(w in text for w in ["হারালে", "হারিয়ে", "হারিয়ে", "harano", "hariye"]):
        if has_procedure_signal:
            bump("procedure_inquiry", 40)
            bump("lost_document", 28)
        else:
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
    if hits.get("application") or any(
        w in text for w in ["korte chai", "apply", "new passport", "new e-passport"]
    ):
        if "ke pare" not in text and "ke korte pare" not in text and "who can" not in text:
            bump("application", 30)
    if any(w in text for w in ["korte chai", "korbo", "korte hobe"]) and "status" not in text:
        if has_document_signal:
            bump("document_list", 25)
        elif "ke pare" not in text and "ke korte pare" not in text:
            bump("application", 20)
    if re.search(r"\bnew\b", text) and any(
        w in text for w in ["korte chai", "korbo", "passport", "e-passport", "e passport"]
    ):
        bump("application", 40)

    # Documents / requirements — beats processing_time for first-time queries
    if has_document_signal:
        bump("document_list", 38)

    # Procedure / how-to
    if has_procedure_signal:
        bump("procedure_inquiry", 28)

    # Processing time — only when explicit SLA/time question, not bare "first time"
    time_markers = [
        "processing time",
        "how long",
        "koto din",
        "কত দিন",
        "sla",
        "weeks",
        "months",
    ]
    if any(w in text for w in time_markers):
        bump("processing_time", 30)
    elif re.search(r"\b\d+\s*(day|days|week|weeks)\b", text):
        bump("processing_time", 28)
    elif "time" in text.split() and not has_document_signal:
        # Avoid "first time" → processing_time unless other time context exists
        if any(w in text for w in ["processing", "take", "long", "delivery"]):
            bump("processing_time", 22)

    # Education certificate verification (not BDRIS/police)
    if any(w in text for w in ["ssc", "hsc", "transcript"]) and "verification" in text:
        bump("general_info", 42)
    if any(w in text for w in ["difference", " vs ", "compare", "mrp naki", "naki e-passport"]):
        bump("comparison", 25)

    # Verification portal questions
    if any(w in text for w in ["verify", "verification", "everify", "যাচাই"]):
        if "everify" in text or "bdris" in text:
            bump("general_info", 30)
        bump("procedure_inquiry", 12)

    # Online account registration flows
    if "registration" in text and any(w in text for w in ["online", "account", "portal"]):
        bump("procedure_inquiry", 30)
        bump("application_url", 10)

    # New application URL questions
    if any(w in text for w in ["apply online", "application url", "onboarding", "আবেদন কোথায়", "কোথায়"]):
        if any(w in text for w in ["passport", "e-passport", "epassport", "ই-পাসপোর্ট", "পাসপোর্ট"]):
            bump("application_url", 40)
            bump("application", 25)

    # Mission / abroad context
    if hits.get("mission"):
        bump("renewal", 10)
        bump("procedure_inquiry", 10)

    # Police verification SLA / charter
    if any(w in text for w in ["police verification", "police verif", "pv", "পুলিশ ভেরিফিকেশন"]):
        if any(w in text for w in ["sla", "charter", "timeline", "processing time", "koto din"]):
            bump("processing_time", 45)
            bump("procedure_inquiry", 10)
        else:
            bump("procedure_inquiry", 25)

    # Clarification overrides
    if clarifications.get("passport_type") == "mrp":
        bump("comparison", 5)
    if clarifications.get("application_type") in {"renewal", "reissue"}:
        bump("renewal", 15)
        bump("reissue", 15)
    if clarifications.get("correction_type") == "dob":
        bump("fee_inquiry", 10)
        bump("correction", 10)
    if clarifications.get("correction_type") == "name":
        bump("fee_inquiry", 10)
        bump("correction", 10)

    if not scored:
        # Domain keyword fallback
        if any(w in text for w in ["passport", "nid", "brta", "tin", "birth", "death", "জন্ম", "মৃত্যু", "এনআইডি"]):
            return IntentResult(primary="document_list")
        return IntentResult(primary="general_info")

    ranked = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)
    primary = ranked[0][0]
    secondary = [intent for intent, score in ranked[1:] if score >= ranked[0][1] * 0.6]

    # Multi-intent: fee + documents commonly co-occur
    if "fee_inquiry" in scored and "document_list" in scored:
        if "document_list" not in [primary, *secondary] and scored["document_list"] >= 30:
            secondary.append("document_list")
        if primary != "fee_inquiry" and scored.get("fee_inquiry", 0) >= 30:
            secondary.append("fee_inquiry")

    return IntentResult(primary=primary, secondary=secondary)


def classify_intent(message: str, clarifications: dict[str, Any] | None = None) -> str:
    """Backward-compatible single-intent classifier returning legacy alias."""
    return classify_intents(message, clarifications).legacy_primary()
