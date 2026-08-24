"""Canonical intent taxonomy shared by classifier, orchestrator, and evaluators."""

from __future__ import annotations

from app.ai.routing.loader import load_intent_taxonomy

# Evaluator-facing aliases → canonical intent id (from intent_taxonomy.json keys).
INTENT_EQUIVALENTS: dict[str, set[str]] = {
    "fee_inquiry": {"fee_inquiry"},
    "document_list": {"document_list"},
    "procedure_inquiry": {
        "procedure_inquiry",
        "application",
        "status",
        "payment",
        "lost_document",
        "damaged_document",
        "application_url",
    },
    "general_info": {
        "general_info",
        "application_url",
        "comparison",
        "service_discovery",
        "processing_time",
    },
    "eligibility": {"eligibility", "eligibility_inquiry", "validity"},
    "eligibility_inquiry": {"eligibility", "eligibility_inquiry", "validity"},
    "validity": {"validity", "eligibility", "eligibility_inquiry"},
    "office_locator": {"office_locator"},
    "processing_time": {"processing_time"},
    "appointment": {"appointment"},
    "correction": {"correction"},
    "renewal": {"renewal", "reissue"},
    "reissue": {"reissue", "renewal"},
    "lost_document": {"lost_document", "damaged_document", "procedure_inquiry"},
    "contact": {"contact"},
    "practical_guidance": {"practical_guidance"},
}


def canonical_intent(name: str | None) -> str:
    """Map any intent label to its canonical evaluator id."""
    if not name:
        return "general_info"
    taxonomy = load_intent_taxonomy()
    if name in taxonomy.get("intents", {}):
        return name
    for canonical, aliases in INTENT_EQUIVALENTS.items():
        if name in aliases:
            return canonical
    # legacy_alias reverse lookup
    for intent_id, entry in taxonomy.get("intents", {}).items():
        if entry.get("legacy_alias") == name:
            return intent_id
    return name


def expand_intent_accept(*names: str) -> set[str]:
    """Expand expected intents to all equivalent labels for comparison."""
    expanded: set[str] = set()
    for name in names:
        expanded.add(name)
        expanded.add(canonical_intent(name))
        expanded.update(INTENT_EQUIVALENTS.get(canonical_intent(name), {name}))
        entry = load_intent_taxonomy().get("intents", {}).get(canonical_intent(name), {})
        legacy = entry.get("legacy_alias")
        if legacy:
            expanded.add(str(legacy))
    return expanded


def intent_matches(
    expected: str,
    actual: str,
    *,
    accept: set[str] | None = None,
    secondary: list[str] | None = None,
) -> bool:
    """Return True when actual intent satisfies expected (canonical-aware)."""
    allowed = expand_intent_accept(expected)
    if accept:
        allowed |= expand_intent_accept(*accept)
    actual_labels = {actual, canonical_intent(actual)}
    if secondary:
        actual_labels |= {canonical_intent(s) for s in secondary}
        for s in secondary:
            actual_labels.add(s)
            entry = load_intent_taxonomy().get("intents", {}).get(s, {})
            legacy = entry.get("legacy_alias")
            if legacy:
                actual_labels.add(str(legacy))
    return bool(actual_labels & allowed)


def public_intent(primary: str, secondary: list[str] | None = None) -> str:
    """Intent label exposed to clients/evaluators (legacy taxonomy)."""
    secondary = secondary or []
    taxonomy = load_intent_taxonomy()
    entry = taxonomy.get("intents", {}).get(primary, {})
    legacy = str(entry.get("legacy_alias") or primary)

    # Procedure-style lost/damaged queries report procedure_inquiry
    if primary in {"lost_document", "damaged_document"} and "procedure_inquiry" in secondary:
        return "procedure_inquiry"
    if primary == "lost_document" and any(
        s in secondary for s in {"procedure_inquiry", "reissue", "renewal"}
    ):
        return "procedure_inquiry"

    # Verification portal availability → general_info
    if primary == "procedure_inquiry" and "general_info" in secondary:
        return "general_info"

    # Explicit URL/portal requests stay application_url
    if primary == "application_url":
        return "application_url"

    # List/download official URL availability

    if primary in {"application", "procedure_inquiry"} and "eligibility" in secondary:
        return "eligibility_inquiry"

    if primary in {"validity", "eligibility"}:
        return "eligibility_inquiry"

    if primary == "processing_time":
        return "processing_time"

    if primary == "comparison":
        return "general_info"

    return legacy
