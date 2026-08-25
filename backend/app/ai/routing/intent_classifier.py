"""Expanded intent classification with multi-intent support."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.ai.routing.loader import load_capability_aliases, load_intent_taxonomy
from app.ai.routing.semantic_phrases import detect_semantic_signals


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


def classify_intents(
    message: str,
    clarifications: dict[str, Any] | None = None,
    *,
    raw_message: str | None = None,
) -> IntentResult:
    """Classify primary and secondary intents from normalized or raw message."""
    text = message.lower()
    clarifications = clarifications or {}
    raw = (raw_message or message).lower()
    signals = detect_semantic_signals(text, raw)
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

    # Fee inquiry — strong signal (skip when time/validity semantics present)
    if not signals.processing_time and not signals.validity:
        if hits.get("fee") or re.search(r"\b(free|ফ্রি)\b", text):
            bump("fee_inquiry", 40)
        if hits.get("fee") or re.search(r"\b\d{2,5}\s*(bdt|taka|টাকা)?\b", text):
            if hits.get("fee") or re.search(r"\b\d{2,5}\s*(bdt|taka)\b", text):
                bump("fee_inquiry", 40)
    if re.search(r"কত\s*টাকা", raw) or re.search(r"kot[oa]\s*taka", text):
        bump("fee_inquiry", 45)

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

    # Application URL — prefer over office_locator when asking where to apply online
    url_list_query = any(w in text for w in ["list", "download"]) and any(
        w in text for w in ["url", "official", "website", "portal"]
    )
    if url_list_query and not any(w in text for w in ["apply", "application", "register", "onboarding"]):
        bump("general_info", 35)
    elif signals.url_request or (
        signals.application_location and not signals.physical_office
    ):
        bump("application_url", 45)
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
        if signals.application_location or ("application" in text or "apply" in text or "visa" in text):
            bump("application_url", 40)
        else:
            bump("application_url", 35)

    # Status
    if hits.get("status") or any(w in text for w in ["status check", "tracking", "track", "kotodur"]):
        bump("status", 40)

    # Appointment
    if hits.get("appointment"):
        bump("appointment", 40)

    # Office / location — physical office only; application location handled above
    if signals.physical_office or (
        signals.location
        and not signals.application_location
        and not signals.url_request
        and not ("application" in text or "apply" in text or "visa application" in text)
    ):
        if any(
            w in text
            for w in ["where", "kothay", "office", "location", "কোথায়", "কোথায়", "অফিস", "ঠিকানা"]
        ):
            bump("office_locator", 35)
    elif "address" in text and not any(
        w in text for w in ["eligible", "eligibility", "only for", "who can", "can i"]
    ):
        bump("office_locator", 20)

    # Validity / eligibility duration (beats processing_time when "valid" present)
    if signals.validity:
        bump("validity", 50)
        bump("eligibility", 45)

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
    lost_context = hits.get("lost") or any(
        w in text for w in ["হারালে", "হারিয়ে", "হারিয়ে", "harano", "hariye", "stolen", "missing passport"]
    )
    gd_context = hits.get("general_diary") or re.search(r"\bgd\b", text)
    if hits.get("lost") and lost_context and not (gd_context and not lost_context):
        if has_procedure_signal:
            bump("procedure_inquiry", 42)
            bump("lost_document", 30)
        else:
            bump("lost_document", 40)
    if any(w in text for w in ["হারালে", "হারিয়ে", "হারিয়ে", "harano", "hariye"]) and not gd_context:
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

    # Documents / requirements — not when GD procedure or overview query
    if has_document_signal and not signals.overview:
        if gd_context and (has_procedure_signal or "online" in text) and "lost" in text:
            bump("procedure_inquiry", 35)
        else:
            bump("document_list", 38)

    # Procedure / how-to
    if has_procedure_signal or signals.procedure:
        bump("procedure_inquiry", 28)

    # Overview / responsibility queries
    if signals.overview:
        bump("general_info", 48)

    # Comparison queries
    if signals.comparison or hits.get("comparison"):
        bump("comparison", 45)
        bump("general_info", 30)

    # General Diary (distinct from lost-passport GD context)
    if gd_context and not lost_context:
        bump("procedure_inquiry", 42)
        if hits.get("feasibility") or any(
            w in text for w in ["kora jay", "procedure inquiry", "can i", "is it possible", "allowed"]
        ):
            bump("procedure_inquiry", 12)
            bump("eligibility", 8)
    elif gd_context and "online" in text and "lost" in text:
        bump("procedure_inquiry", 48)

    # Processing time — explicit phrase wins; semantic time beats generic procedure
    time_markers = [
        "processing time",
        "how long",
        "koto din",
        "কত দিন",
        "sla",
        "weeks",
        "months",
        "lage",
        "লাগ",
    ]
    if signals.processing_time or "processing time" in text:
        bump("processing_time", 55)
    elif any(w in raw for w in time_markers) or any(w in text for w in time_markers):
        if not signals.validity:
            bump("processing_time", 35)
    elif re.search(r"\b\d+\s*(day|days|week|weeks)\b", text):
        bump("processing_time", 28)
    elif "time" in text.split() and not has_document_signal:
        if any(w in text for w in ["processing", "take", "long", "delivery"]):
            bump("processing_time", 22)

    # Passport/police verification SLA queries
    if hits.get("passport_verification_sla") or (
        "passport verification" in text and ("processing time" in text or "koto din" in text)
    ):
        bump("processing_time", 40)

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

    # Where to complete a procedure (office/thana), not portal URL lookup
    if signals.location and not signals.url_request and not signals.application_location:
        if any(w in text for w in ("korte hobe", "korte hoy", "korbo", "verification office")):
            bump("procedure_inquiry", 40)
        elif "verification" in text and "office" in text:
            bump("procedure_inquiry", 35)

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
    if any(w in text for w in ["police verification", "police verif", "pv", "পুলিশ ভেরিফিকেশন"]) or (
        "passport verification" in text and "police" in text
    ):
        if any(w in text for w in ["sla", "charter", "timeline", "processing time", "koto din"]):
            bump("processing_time", 45)
            bump("procedure_inquiry", 10)
        else:
            bump("procedure_inquiry", 25)

    # Clarification overrides
    if clarifications.get("channel") and clarifications.get("service") == "police-clearance-certificate":
        bump("fee_inquiry", 50)
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

    # Explicit processing-time phrase must beat generic verification→procedure signal
    if (signals.processing_time or "processing time" in text) and scored.get("processing_time", 0) >= 30:
        if scored.get("procedure_inquiry", 0) > scored.get("processing_time", 0):
            primary = "processing_time"

    # Validity beats processing_time when both scored
    if signals.validity and scored.get("validity", 0) >= scored.get("processing_time", 0):
        primary = "validity" if scored.get("validity", 0) >= scored.get("eligibility", 0) else "eligibility"

    # Application URL beats office_locator for apply/visa location questions
    if signals.application_location and scored.get("application_url", 0) >= 35:
        if scored.get("office_locator", 0) > scored.get("application_url", 0):
            primary = "application_url"

    # URL request beats procedure
    if signals.url_request and scored.get("application_url", 0) >= 30:
        primary = "application_url"

    # Overview beats document_list
    if signals.overview and scored.get("general_info", 0) >= 40:
        primary = "general_info"

    # Comparison beats procedure
    if signals.comparison and scored.get("comparison", 0) >= 40:
        primary = "comparison"

    # Procedure location beats office_locator for verification/thana queries
    if signals.location and not signals.application_location and not signals.url_request:
        if scored.get("procedure_inquiry", 0) >= 35 and scored.get("procedure_inquiry", 0) >= scored.get(
            "office_locator", 0
        ):
            primary = "procedure_inquiry"

    # GD online lost-item filing — procedure, not document list
    if gd_context and "online" in text and "lost" in text and scored.get("procedure_inquiry", 0) >= 40:
        primary = "procedure_inquiry"

    secondary = [
        intent
        for intent, score in ranked
        if intent != primary and score >= scored.get(primary, ranked[0][1]) * 0.6
    ]

    # Multi-intent: fee + documents commonly co-occur
    if "fee_inquiry" in scored and "document_list" in scored:
        if "document_list" not in [primary, *secondary] and scored["document_list"] >= 30:
            secondary.append("document_list")
        if primary != "fee_inquiry" and scored.get("fee_inquiry", 0) >= 30:
            secondary.append("fee_inquiry")

    return IntentResult(primary=primary, secondary=secondary)


def classify_intent(
    message: str,
    clarifications: dict[str, Any] | None = None,
    *,
    raw_message: str | None = None,
) -> str:
    """Backward-compatible single-intent classifier returning legacy alias."""
    return classify_intents(message, clarifications, raw_message=raw_message).legacy_primary()
