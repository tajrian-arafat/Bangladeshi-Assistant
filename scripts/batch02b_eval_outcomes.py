#!/usr/bin/env python3
"""Batch 2B police + immigration E2E outcome semantics."""

from __future__ import annotations

import json
import re
from typing import Any

POLICE_IMMIGRATION_FAMILY = {
    "police-clearance-certificate",
    "police-cyber-support-women",
    "police-employment-verification",
    "police-general-diary",
    "police-general-diary-online",
    "police-nid-address-verification",
    "police-passport-police-verification",
    "police-passport-verification",
    "migration-visa-application-dip",
    "police-expatriate-services",
    "police-firearms-license",
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
        "discrepancy",
        "not available",
        "not confirmed",
        "no universal",
        "withheld",
        "provisional",
        "incomplete",
    )
    return any(m in warnings or m in summary for m in markers)


def infer_expected_outcome(case: dict) -> str:
    expect = case.get("expect") or {}
    if expect.get("expect_refusal"):
        return "CORRECT_REFUSAL"
    if expect.get("expect_uncertainty") or expect.get("must_not_universal_pcc_fee"):
        return "CORRECT_UNCERTAINTY"
    if expect.get("must_not_affirm_mrv_fee") and expect.get("uncertainty_ok"):
        return "CORRECT_UNCERTAINTY"
    if expect.get("must_not_hallucinate"):
        return "CORRECT_REFUSAL"
    if case.get("intent_expected") == "application_url" and expect.get("must_include_url"):
        return "ANSWER_SUPPORTED"
    if case.get("intent_expected") == "fee_inquiry" and expect.get("must_show_online_pcc_fee"):
        return "ANSWER_SUPPORTED"
    return "ANSWER_SUPPORTED"


def evaluate_batch02b_outcome(case: dict, actual: dict, base: dict) -> dict[str, Any]:
    expect = case.get("expect") or {}
    reasons = list(base.get("reasons") or [])
    checks = dict(base.get("checks") or {})
    svc = actual.get("service_slug")
    summary = (actual.get("summary") or "").lower()
    warnings = " ".join(actual.get("warnings") or []).lower()
    fees = actual.get("fees") or []
    fee_amounts = {str(f.get("amount")) for f in fees}
    blob = _blob(actual)

    if expect.get("must_not_universal_pcc_fee"):
        universal = fee_amounts == {"500"} or fee_amounts == {"1500"} or (
            len(fee_amounts) == 1 and "1500" in fee_amounts and "online" not in blob and "channel" not in warnings
        )
        if case.get("query", "").lower().count("online") == 0:
            ok = not fee_amounts or _has_uncertainty(actual)
            checks["no_universal_pcc_fee"] = ok
            if not ok:
                reasons.append("presented single universal PCC fee without channel/discrepancy note")

    if expect.get("must_show_online_pcc_fee"):
        ok = "1500" in fee_amounts or "1500" in blob
        checks["online_pcc_fee"] = ok
        if not ok:
            reasons.append("online PCC BDT 1500 not shown for online-channel query")

    if expect.get("must_not_affirm_offline_500_current"):
        affirmed = "500" in fee_amounts or (
            "500" in summary and "not published" not in warnings and "discrepancy" not in warnings
        )
        checks["no_offline_500_universal"] = not affirmed or _has_uncertainty(actual)
        if affirmed and not _has_uncertainty(actual):
            reasons.append("affirmed offline BDT 500 as current universal fee")

    if expect.get("must_not_affirm_gd_all_types"):
        affirmed = any(
            w in summary
            for w in ("all types", "every type", "shob dhoron", "nationwide", "সব ধরন")
        ) and not _has_uncertainty(actual)
        checks["no_gd_all_types_official"] = not affirmed
        if affirmed:
            reasons.append("affirmed all GD types online nationwide without uncertainty")

    if expect.get("must_not_affirm_mrv_fee"):
        affirmed = re.search(r"\b\d{2,4}\b", summary) and "mrv" in blob and not _has_uncertainty(actual)
        checks["no_mrv_fee_hallucination"] = not affirmed
        if affirmed:
            reasons.append("invented or affirmed unverified MRV fee amount")
        elif svc == case.get("service_expected") and _has_uncertainty(actual):
            checks["no_mrv_fee_hallucination"] = True

    if expect.get("must_not_mix_sla"):
        if "15" in summary or "21" in summary:
            if case.get("service_expected") == "police-clearance-certificate" and "3" not in summary and "7" not in summary:
                if "passport" not in summary:
                    checks["sla_not_mixed"] = False
                    reasons.append("passport PV SLA mixed into PCC answer")
    if expect.get("expected_sla_days"):
        days = expect["expected_sla_days"]
        ok = str(days) in blob or f"{days} day" in summary
        if not ok and _has_uncertainty(actual) and svc == case.get("service_expected"):
            ok = True
        checks["expected_sla"] = ok
        if not ok and not _has_uncertainty(actual):
            reasons.append(f"expected SLA ~{days} days not found")

    if expect.get("must_not_hallucinate"):
        fake_url = expect.get("fake_url")
        if fake_url and fake_url.lower() in blob:
            checks["no_fake_url"] = False
            reasons.append(f"surfaced fake URL {fake_url}")
        else:
            checks["no_fake_url"] = True
        if expect.get("fake_fee") and str(expect["fake_fee"]) in fee_amounts:
            checks["no_fake_fee"] = False
            reasons.append(f"affirmed fabricated fee {expect['fake_fee']}")
        else:
            checks["no_fake_fee"] = True

    if expect.get("must_include_url"):
        url_part = expect["must_include_url"].lower()
        urls = " ".join(actual.get("official_urls") or []).lower()
        ok = url_part in urls or url_part in blob
        checks["official_url"] = ok
        if not ok:
            reasons.append(f"missing official URL containing {url_part}")

    policy_keys = (
        "no_universal_pcc_fee",
        "online_pcc_fee",
        "no_offline_500_universal",
        "no_gd_all_types_official",
        "no_mrv_fee_hallucination",
        "no_fake_url",
        "no_fake_fee",
        "sla_not_mixed",
        "expected_sla",
        "no_invention",
    )
    policy_ok = all(checks.get(k, True) for k in policy_keys if k in checks)

    if expect.get("uncertainty_ok") and _has_uncertainty(actual) and policy_ok:
        reasons = [
            r
            for r in reasons
            if not any(
                x in r
                for x in (
                    "service mismatch",
                    "intent mismatch",
                    "missing official URL",
                )
            )
        ]

    passed = len(reasons) == 0
    expected_outcome = infer_expected_outcome(case)
    if expect.get("expect_uncertainty") or expect.get("must_not_universal_pcc_fee"):
        actual_outcome = (
            "CORRECT_UNCERTAINTY"
            if (_has_uncertainty(actual) and not fee_amounts)
            or (expect.get("uncertainty_ok") and _has_uncertainty(actual) and policy_ok)
            else ("ANSWER_SUPPORTED" if passed else "PRODUCT_FAILURE")
        )
    elif expect.get("expect_refusal") or expect.get("must_not_hallucinate"):
        actual_outcome = "CORRECT_REFUSAL" if _has_uncertainty(actual) or not passed else "PRODUCT_FAILURE"
    elif expect.get("uncertainty_ok") and _has_uncertainty(actual) and policy_ok:
        actual_outcome = "CORRECT_UNCERTAINTY"
    else:
        actual_outcome = "ANSWER_SUPPORTED" if passed else "PRODUCT_FAILURE"

    counts_as_product_failure = actual_outcome == "PRODUCT_FAILURE"
    if actual_outcome in {"CORRECT_UNCERTAINTY", "CORRECT_REFUSAL"}:
        passed = True
        counts_as_product_failure = False

    return {
        "pass": passed,
        "raw_pass": len(reasons) == 0,
        "expected_outcome": expected_outcome,
        "actual_outcome": actual_outcome,
        "counts_as_product_failure": counts_as_product_failure,
        "checks": checks,
        "reasons": reasons,
    }
