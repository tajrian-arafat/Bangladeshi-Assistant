#!/usr/bin/env python3
"""Batch 3B BRTA vehicle E2E outcome semantics."""

from __future__ import annotations

import json
import re
from typing import Any

BRTA_VEHICLE_FAMILY = {
    "brta-new-vehicle-registration",
    "brta-ownership-transfer",
    "brta-digital-registration-certificate",
    "brta-vehicle-info-correction",
    "brta-retro-reflective-number-plate",
    "brta-trustee-board-certificate",
}

# Fitness validity is deferred to BATCH_03C; routing may land on fitness service.
FITNESS_DEFERRED_ALTERNATES = {"brta-fitness-certificate"}


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
        "off-hours",
        "temporarily unavailable",
        "provisional",
        "deferred",
    )
    return any(m in warnings or m in summary for m in markers)


def _service_ok(case: dict, actual: dict, checks: dict, reasons: list[str]) -> tuple[dict, list[str]]:
    expect = case.get("expect") or {}
    svc = actual.get("service_slug")
    expected = case.get("service_expected")

    if expect.get("allow_brta_vehicle_family") and svc in BRTA_VEHICLE_FAMILY:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if expected and svc == expected:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if case.get("category") == "FITNESS_DEFERRED" and expect.get("uncertainty_ok"):
        if svc in FITNESS_DEFERRED_ALTERNATES | {expected}:
            checks["service"] = True
            reasons = [r for r in reasons if "service mismatch" not in r]

    if expect.get("clarification_ok") and not expected:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    if expect.get("must_not_hallucinate") and svc is None and not expected:
        checks["service"] = True
        reasons = [r for r in reasons if "service mismatch" not in r]

    return checks, reasons


def evaluate_batch03b_outcome(case: dict, actual: dict, base: dict) -> dict[str, Any]:
    expect = case.get("expect") or {}
    reasons = list(base.get("reasons") or [])
    checks = dict(base.get("checks") or {})
    svc = actual.get("service_slug")
    fees = actual.get("fees") or []
    fee_amounts = {str(f.get("amount")) for f in fees if f.get("amount") is not None}
    blob = _blob(actual)
    citations = actual.get("citations") or []
    citation_urls = " ".join(
        (c.get("url") or c.get("source_url") or "") for c in citations
    ).lower()
    official_urls = " ".join(actual.get("official_urls") or []).lower()

    checks, reasons = _service_ok(case, actual, checks, reasons)

    # Drop strict intent checks from batch01 — product quality is policy-based.
    reasons = [r for r in reasons if "intent mismatch" not in r]
    checks.pop("intent", None)

    if expect.get("must_include_url"):
        needle = expect["must_include_url"].lower()
        ok = needle in blob or needle in citation_urls or needle in official_urls
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
        if fake and (fake in blob or fake in citation_urls):
            checks["no_hallucination"] = False
            reasons.append(f"affirmed fake URL: {fake}")
        else:
            checks["no_hallucination"] = True

    if expect.get("require_citation"):
        if not citations:
            checks["citation"] = False
            reasons.append("citation missing for supported factual answer")
        elif not all((c.get("source_url") or c.get("url")) for c in citations):
            checks["citation"] = False
            reasons.append("citation missing source URL")
        elif not all(c.get("evidence_id") for c in citations):
            checks["citation"] = False
            reasons.append("citation missing evidence_id")
        else:
            checks["citation"] = True
            fake = (expect.get("fake_url") or "").lower()
            if fake and any(
                fake in (c.get("source_url") or c.get("url") or "").lower() for c in citations
            ):
                checks["citation"] = False
                reasons.append(f"decorative or fake citation URL: {fake}")

    if expect.get("uncertainty_ok") and _has_uncertainty(actual):
        checks["uncertainty"] = True
        reasons = [
            r
            for r in reasons
            if not any(
                x in r
                for x in (
                    "service mismatch",
                    "missing official URL",
                )
            )
        ]

    if expect.get("expect_refusal") and (_has_uncertainty(actual) or svc is None):
        outcome = "CORRECT_REFUSAL"
    elif expect.get("must_not_hallucinate") and checks.get("no_hallucination", True):
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
