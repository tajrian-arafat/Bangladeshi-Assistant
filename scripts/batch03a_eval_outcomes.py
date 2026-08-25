#!/usr/bin/env python3
"""Batch 3A BRTA driving licence E2E outcome semantics."""

from __future__ import annotations

import json
import re
from typing import Any

BRTA_DRIVING_LICENCE_FAMILY = {
    "brta-learner-driving-license",
    "brta-driving-license-renewal",
    "brta-duplicate-driving-license",
    "brta-smart-card-driving-license",
    "brta-driving-instructor-license",
    "brta-dctc-exam-result",
    "driving-licence-renewal",
}


def _blob(actual: dict) -> str:
    return json.dumps(actual, ensure_ascii=False).lower()


def _has_uncertainty(actual: dict) -> bool:
    warnings = " ".join(actual.get("warnings") or []).lower()
    summary = (actual.get("summary") or "").lower()
    markers = (
        "not verified",
        "uncertain",
        "conflict",
        "not available",
        "not confirmed",
        "calculator",
        "vary",
        "depends",
    )
    return any(m in warnings or m in summary for m in markers)


def evaluate_batch03a_outcome(case: dict, actual: dict, base: dict) -> dict[str, Any]:
    expect = case.get("expect") or {}
    reasons = list(base.get("reasons") or [])
    checks = dict(base.get("checks") or {})
    svc = actual.get("service_slug")
    summary = (actual.get("summary") or "").lower()
    warnings = " ".join(actual.get("warnings") or []).lower()
    fees = actual.get("fees") or []
    fee_amounts = {str(f.get("amount")) for f in fees if f.get("amount") is not None}
    blob = _blob(actual)
    citations = actual.get("citations") or []
    citation_urls = " ".join(
        (c.get("url") or c.get("source_url") or "") for c in citations
    ).lower()

    if expect.get("allow_brta_driving_family") and svc in BRTA_DRIVING_LICENCE_FAMILY:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if case.get("service_expected") and svc == case["service_expected"]:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if expect.get("must_include_url"):
        needle = expect["must_include_url"].lower()
        ok = needle in blob or needle in citation_urls
        checks["official_url"] = ok
        if not ok:
            reasons.append(f"missing official URL fragment: {expect['must_include_url']}")

    if expect.get("must_not_invent_fee"):
        reject = expect.get("must_reject_amount")
        if reject and reject in fee_amounts:
            checks["no_invented_fee"] = False
            reasons.append(f"affirmed unverified fee amount {reject}")
        elif fee_amounts and not _has_uncertainty(actual):
            checks["no_invented_fee"] = False
            reasons.append("presented specific fee without uncertainty/calculator note")
        else:
            checks["no_invented_fee"] = True

    if expect.get("must_not_hallucinate"):
        fake = (expect.get("fake_url") or "").lower()
        if fake and fake in blob:
            checks["no_hallucination"] = False
            reasons.append(f"affirmed fake URL: {fake}")
        else:
            checks["no_hallucination"] = True

    if expect.get("must_mention_bsp_register"):
        ok = "register" in blob or "registration" in summary
        checks["bsp_register"] = ok
        if not ok:
            reasons.append("BSP registration prerequisite not mentioned")

    if expect.get("must_mention_dctc"):
        ok = "dctc" in blob or "dctb" in blob or "driving test" in summary
        checks["dctc_mention"] = ok
        if not ok:
            reasons.append("DCTC examination pathway not mentioned")

    if expect.get("uncertainty_ok") and _has_uncertainty(actual):
        checks["uncertainty"] = True

    if expect.get("expect_refusal") and _has_uncertainty(actual):
        outcome = "CORRECT_REFUSAL"
    elif expect.get("uncertainty_ok") and _has_uncertainty(actual):
        outcome = "CORRECT_UNCERTAINTY"
    elif all(checks.get(k, True) for k in checks):
        outcome = "ANSWER_SUPPORTED"
    else:
        outcome = "PRODUCT_FAILURE"

    raw_pass = outcome == "ANSWER_SUPPORTED"
    pass_norm = outcome in {"ANSWER_SUPPORTED", "CORRECT_UNCERTAINTY", "CORRECT_REFUSAL"}
    product_failure = outcome == "PRODUCT_FAILURE"

    return {
        "pass": pass_norm,
        "raw_pass": raw_pass,
        "expected_outcome": case.get("expected_outcome", "ANSWER_SUPPORTED"),
        "actual_outcome": outcome,
        "counts_as_product_failure": product_failure,
        "checks": checks,
        "reasons": reasons,
    }
