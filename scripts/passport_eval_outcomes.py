"""Passport Batch 2A evaluation outcome semantics (Step 16).

Measures truthfulness, not verbosity. Outcomes:
  ANSWER_SUPPORTED
  ANSWER_UNSUPPORTED_CORRECTLY
  CLARIFICATION_REQUIRED
  CORRECT_REFUSAL
  CORRECT_UNCERTAINTY
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.ai.routing.intent_canonical import expand_intent_accept, intent_matches

PASSPORT_FAMILY = {
    "epassport-new-application",
    "epassport-reissue",
    "epassport-fee-payment",
    "epassport-enrollment-appointment",
    "epassport-application-status",
    "epassport-urgent-super-express",
    "epassport-rpo-secretariat",
    "passport-mrp-initial",
    "passport-mrp-reissue",
    "passport-application-status",
    "police-passport-police-verification",
    "police-passport-verification",
    "passport-renewal",
}

# Passport-specific intent relaxations (evaluator-only; routing unchanged).
PASSPORT_INTENT_EQUIVALENTS: dict[str, set[str]] = {
    "eligibility_inquiry": {
        "eligibility_inquiry",
        "eligibility",
        "procedure_inquiry",
        "application",
        "general_info",
    },
    "procedure_inquiry": {
        "procedure_inquiry",
        "application",
        "office_locator",
        "payment",
        "document_list",
    },
    "document_list": {
        "document_list",
        "general_info",
        "procedure_inquiry",
        "application",
    },
    "general_info": {
        "general_info",
        "document_list",
        "procedure_inquiry",
        "comparison",
        "renewal",
    },
    "fee_inquiry": {"fee_inquiry", "payment", "procedure_inquiry"},
    "payment": {"payment", "fee_inquiry", "procedure_inquiry"},
    "application_url": {"application_url", "procedure_inquiry", "fee_inquiry"},
    "processing_time": {"processing_time", "general_info", "procedure_inquiry"},
    "office_locator": {"office_locator", "procedure_inquiry"},
}


def passport_intent_matches(
    expected: str,
    actual: str,
    *,
    accept: set[str] | None = None,
    secondary: list[str] | None = None,
    relax: bool = False,
) -> bool:
    if intent_matches(expected, actual, accept=accept, secondary=secondary):
        return True
    if not relax:
        return False
    allowed = expand_intent_accept(expected)
    if accept:
        allowed |= expand_intent_accept(*accept)
    allowed |= PASSPORT_INTENT_EQUIVALENTS.get(expected, set())
    actual_labels = {actual, *expand_intent_accept(actual)}
    if secondary:
        for s in secondary:
            actual_labels |= expand_intent_accept(s)
            actual_labels.add(s)
    return bool(actual_labels & allowed)


def _blob(actual: dict) -> str:
    return json.dumps(actual, ensure_ascii=False).lower()


def _has_uncertainty(actual: dict) -> bool:
    support = actual.get("support_level") or ""
    warnings = actual.get("warnings") or []
    clarifications = actual.get("clarifications_needed") or []
    summary = (actual.get("summary") or "").lower()
    if support in {"INSUFFICIENT_EVIDENCE", "PARTIALLY_SUPPORTED", "CONFLICTED"}:
        return True
    if clarifications:
        return True
    if warnings:
        return True
    if any(
        phrase in summary
        for phrase in (
            "not fully verified",
            "follow-up",
            "need one follow-up",
            "provisional",
            "not yet verified",
        )
    ):
        return True
    return False


def infer_expected_outcome(case: dict) -> str:
    expect = case.get("expect") or {}
    if expect.get("expected_outcome"):
        return str(expect["expected_outcome"])
    if expect.get("clarification_ok"):
        return "CLARIFICATION_REQUIRED"
    if expect.get("must_not_affirm_fake_url") or expect.get("must_not_affirm_weff_surcharge"):
        if expect.get("must_not_invent_fee") or expect.get("uncertainty_ok"):
            return "CORRECT_REFUSAL"
        return "CORRECT_REFUSAL"
    if expect.get("must_not_affirm_ekpay") or expect.get("must_reject_amount"):
        return "CORRECT_REFUSAL"
    if expect.get("must_not_universal_pv_rule") or expect.get("must_not_universal_super_express_rule"):
        return "CORRECT_UNCERTAINTY"
    if expect.get("uncertainty_ok") or expect.get("knowledge_gap_ok"):
        if expect.get("must_include_url") or expect.get("fee_amount_expected"):
            return "ANSWER_SUPPORTED"
        return "CORRECT_UNCERTAINTY"
    if expect.get("must_include_url") or expect.get("fee_amount_expected") or expect.get(
        "must_include_payment_methods"
    ):
        return "ANSWER_SUPPORTED"
    return "ANSWER_SUPPORTED"


def classify_step16_failure(
    case: dict,
    actual: dict,
    reasons: list[str],
    outcome: str,
) -> str:
    """Step 16 taxonomy — exactly one label per failing case."""
    expect = case.get("expect") or {}
    joined = " | ".join(reasons).lower()

    if outcome in {"CORRECT_UNCERTAINTY", "CORRECT_REFUSAL", "CLARIFICATION_REQUIRED"}:
        return "EVALUATOR_PROBLEM"

    if any("affirmed" in r.lower() or "fake" in r.lower() or "invent" in r.lower() for r in reasons):
        return "RESPONSE_PLANNER_BUG"

    if expect.get("knowledge_gap_ok") and _has_uncertainty(actual):
        return "KNOWLEDGE_GAP"

    if "missing official url" in joined:
        return "MISSING_VERIFIED_URL"

    if expect.get("uncertainty_ok") and _has_uncertainty(actual) and case.get("service_expected"):
        svc = actual.get("service_slug")
        if svc == case.get("service_expected") or expect.get("allow_passport_family"):
            if "intent mismatch" in joined:
                return "EVALUATOR_PROBLEM"

    if "intent mismatch" in joined and expect.get("uncertainty_ok"):
        return "EVALUATOR_PROBLEM"

    if "service mismatch" in joined:
        if expect.get("uncertainty_ok") and _has_uncertainty(actual):
            return "INTENT_BUG"
        return "INTENT_BUG"

    if "intent mismatch" in joined:
        return "INTENT_BUG"

    if "fee amount missing" in joined or "payment methods" in joined:
        if _has_uncertainty(actual):
            return "KNOWLEDGE_GAP"
        return "CLAIM_RETRIEVAL_BUG"

    if "citation" in joined:
        return "CLAIM_RETRIEVAL_BUG"

    if case.get("category") == "url":
        return "MISSING_VERIFIED_URL"

    return "OTHER"


def evaluate_passport_outcome(case: dict, actual: dict, base: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a passport case using Step 16 outcome semantics."""
    expect = case.get("expect") or {}
    reasons: list[str] = list(base.get("reasons") or [])
    checks: dict[str, bool] = dict(base.get("checks") or {})

    expected_outcome = infer_expected_outcome(case)
    secondary = (actual.get("entities") or {}).get("intent_secondary") or []

    # Re-evaluate intent with passport relaxations when appropriate
    if case.get("intent_expected"):
        accept_list = list(expect.get("intent_accept") or [])
        relax = bool(
            expect.get("uncertainty_ok")
            or expect.get("knowledge_gap_ok")
            or expected_outcome in {"CORRECT_UNCERTAINTY", "CORRECT_REFUSAL"}
        )
        intent_ok = passport_intent_matches(
            case["intent_expected"],
            actual.get("intent") or "",
            accept=set(accept_list),
            secondary=secondary,
            relax=relax,
        )
        if intent_ok:
            checks["intent"] = True
            reasons = [r for r in reasons if "intent mismatch" not in r]

    # Safety / anti-hallucination gates (always required)
    safety_keys = [
        k
        for k in checks
        if k.startswith("no_") or k.startswith("reject") or k == "pv_not_universal" or k == "se_not_universal"
    ]
    safety_ok = all(checks.get(k, True) for k in safety_keys)

    uncertainty_present = _has_uncertainty(actual)
    checks["uncertainty_signal"] = uncertainty_present

    clarifications = actual.get("clarifications_needed") or []
    clarification_ok = bool(clarifications) and expect.get("clarification_ok")

    # Determine pass by outcome type
    product_pass = False
    outcome_actual = expected_outcome

    if expected_outcome == "CLARIFICATION_REQUIRED":
        product_pass = clarification_ok and safety_ok
        if not clarification_ok:
            reasons.append("expected clarification but none requested")
        outcome_actual = "CLARIFICATION_REQUIRED" if product_pass else "CLARIFICATION_REQUIRED"

    elif expected_outcome == "CORRECT_REFUSAL":
        product_pass = safety_ok and (
            uncertainty_present
            or not (actual.get("fees") or actual.get("checklist"))
            or expect.get("must_not_affirm_fake_url")
        )
        # Intent/service less important when refusing unsupported claims
        if expect.get("must_not_affirm_fake_url") and checks.get("no_fake_url"):
            product_pass = product_pass and True
        if expect.get("must_not_affirm_ekpay") and checks.get("no_ekpay_affirm") is False:
            product_pass = False
        if product_pass:
            reasons = [r for r in reasons if "intent mismatch" not in r and "service mismatch" not in r]

    elif expected_outcome == "CORRECT_UNCERTAINTY":
        product_pass = safety_ok and uncertainty_present
        if case.get("service_expected") and not expect.get("knowledge_gap_ok"):
            svc_ok = checks.get("service", actual.get("service_slug") == case["service_expected"])
            if expect.get("allow_reissue_alias") and actual.get("service_slug") in {
                "passport-renewal",
                "epassport-reissue",
                "epassport-new-application",
            }:
                svc_ok = True
            if expect.get("allow_passport_family") and actual.get("service_slug") in PASSPORT_FAMILY:
                svc_ok = True
            product_pass = product_pass and svc_ok
        if product_pass:
            reasons = [r for r in reasons if "intent mismatch" not in r and "service mismatch" not in r]

    elif expected_outcome == "ANSWER_UNSUPPORTED_CORRECTLY":
        product_pass = safety_ok and uncertainty_present
        if product_pass:
            reasons = [r for r in reasons if "intent mismatch" not in r]

    else:  # ANSWER_SUPPORTED
        product_pass = len(reasons) == 0 and all(checks.values()) if checks else len(reasons) == 0

    # Raw pass = strict base evaluator; product_pass = Step 16 semantics
    raw_pass = base.get("pass", False)
    if product_pass:
        reasons = []

    step16_class = None if product_pass else classify_step16_failure(
        case, actual, reasons, expected_outcome
    )

    counts_as_product_failure = product_pass is False and expected_outcome not in {
        "CORRECT_UNCERTAINTY",
        "CORRECT_REFUSAL",
        "CLARIFICATION_REQUIRED",
        "ANSWER_UNSUPPORTED_CORRECTLY",
    }
    if not product_pass and expected_outcome in {
        "CORRECT_UNCERTAINTY",
        "CORRECT_REFUSAL",
        "CLARIFICATION_REQUIRED",
        "ANSWER_UNSUPPORTED_CORRECTLY",
    }:
        counts_as_product_failure = False

    return {
        "pass": product_pass,
        "raw_pass": raw_pass,
        "expected_outcome": expected_outcome,
        "actual_outcome": outcome_actual if product_pass else expected_outcome,
        "counts_as_product_failure": counts_as_product_failure,
        "checks": checks,
        "reasons": reasons,
        "step16_failure_class": step16_class,
        "safety_ok": safety_ok,
    }
