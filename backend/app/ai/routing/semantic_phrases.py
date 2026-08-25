"""Reusable Bangla/Banglish/English semantic phrase detection for routing."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.ai.routing.loader import load_capability_aliases


@dataclass
class SemanticSignals:
    location: bool = False
    application_location: bool = False
    physical_office: bool = False
    processing_time: bool = False
    validity: bool = False
    url_request: bool = False
    comparison: bool = False
    overview: bool = False
    document_requirement: bool = False
    procedure: bool = False


_TIME_PATTERNS = [
    r"\bprocessing time\b",
    r"\bhow long\b",
    r"\bkoto din\b",
    r"\bkoto\s+din\s+lage\b",
    r"\bকত\s*দিন\b",
    r"\bকতদিন\b",
    r"\bকত\s*দিন\s*লাগ",
    r"\bsla\b",
    r"\b\d+\s*(day|days|week|weeks)\b",
]

_VALIDITY_PATTERNS = [
    r"\bvalid\b",
    r"\bvalidity\b",
    r"\bvalid koto\b",
    r"\bvalid thakte\b",
    r"\bvalid thakbe\b",
    r"\bexpires?\b",
    r"\bexpiry\b",
    r"\bমেয়াদ\b",
    r"\bমেয়াদ\b",
    r"\bকতদিন\s*valid\b",
    r"\bকতদিন\s*চল\b",
    r"\bthakte hobe\b",
    r"\bthakbe\b",
]

_APPLICATION_LOCATION_PATTERNS = [
    r"\bapplication kothay\b",
    r"\bapply kothay\b",
    r"\bvisa application\b.*\bwhere\b",
    r"\bvisa application\b.*\bkothay\b",
    r"\bআবেদন\s*কোথায়\b",
    r"\bআবেদন\s*কোথায়\b",
    r"\bapply online\b",
    r"\bonline apply\b",
]

_PHYSICAL_OFFICE_PATTERNS = [
    r"\boffice\b",
    r"\bthana\b",
    r"\bspecial branch\b",
    r"\bdistrict sb\b",
    r"\bdsb\b",
    r"\bmsb\b",
    r"\bঅফিস\b",
    r"\bথানা\b",
]

_OVERVIEW_PATTERNS = [
    r"\bresponsible for\b",
    r"\bresponsible aig\b",
    r"\bwhat services\b",
    r"\bservices offered\b",
    r"\bdepartment of\b.*\bwhat\b",
    r"\bcell police services\b",
    r"\bauthority for\b",
]

_COMPARISON_PATTERNS = [
    r"\bsame as\b",
    r"\bdifference\b",
    r"\b vs \b",
    r"\bcompare\b",
    r"\bnaki\b",
]


def _group_tokens(group_name: str) -> list[str]:
    aliases = load_capability_aliases()
    group = aliases.get("capability_groups", {}).get(group_name, {})
    tokens: list[str] = []
    for key in ("synonyms_en", "synonyms_bn", "synonyms_banglish"):
        tokens.extend(group.get(key) or [])
    return [t.lower() for t in tokens if t]


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def detect_semantic_signals(text: str, raw_text: str | None = None) -> SemanticSignals:
    """Detect cross-domain semantic signals from normalized and optional raw text."""
    blob = f"{text} {raw_text or ''}".lower()
    signals = SemanticSignals()

    location_tokens = _group_tokens("location_inquiry")
    signals.location = _matches_any(blob, [re.escape(t) for t in location_tokens if len(t) > 2]) or any(
        w in blob for w in ("where", "kothay", "কোথায়", "কোথায়", "kothay pabo", "কোথায় পাব")
    )

    signals.application_location = (
        _matches_any(blob, _APPLICATION_LOCATION_PATTERNS)
        or ("application" in blob or "apply" in blob or "visa" in blob or "আবেদন" in blob)
        and signals.location
        and not _matches_any(blob, _PHYSICAL_OFFICE_PATTERNS)
    )

    signals.physical_office = _matches_any(blob, _PHYSICAL_OFFICE_PATTERNS)

    time_from_validity = _matches_any(blob, _VALIDITY_PATTERNS) and any(
        w in blob for w in ("valid", "validity", "thakte", "thakbe", "expires", "মেয়াদ", "মেয়াদ", "চল")
    )
    signals.validity = time_from_validity or _matches_any(blob, _VALIDITY_PATTERNS)

    signals.processing_time = (
        _matches_any(blob, _TIME_PATTERNS)
        and not signals.validity
    )

    signals.url_request = any(
        w in blob for w in (" url", "url ", "portal", "website", "online url", "application url", "ওয়েবসাইট", "website")
    ) or blob.strip().endswith("url")

    signals.comparison = _matches_any(blob, _COMPARISON_PATTERNS)
    signals.overview = _matches_any(blob, _OVERVIEW_PATTERNS) or any(
        w in blob for w in ("responsible for", "responsible aig", "what services", "services offered")
    )

    doc_tokens = _group_tokens("document_requirement")
    signals.document_requirement = any(t in blob for t in doc_tokens) or any(
        w in blob for w in ("lagbe", "lage", "required", "documents list", "document list", "কাগজ")
    )

    proc_tokens = _group_tokens("procedure_inquiry")
    signals.procedure = any(t in blob for t in proc_tokens) or any(
        w in blob for w in ("how", "kivabe", "procedure", "kora jay", "apply", "file")
    )

    return signals
