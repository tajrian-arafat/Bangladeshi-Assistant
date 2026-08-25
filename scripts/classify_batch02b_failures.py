#!/usr/bin/env python3
"""Classify all Batch 2B E2E outcomes into normalized outcome buckets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "data/evaluation/batch-02b-police-immigration/results.jsonl"
QUERIES = REPO / "data/evaluation/batch-02b-police-immigration/queries.json"
OUT = REPO / "data/evaluation/batch-02b-police-immigration/failure-classification.json"


def infer_claim_types(case: dict) -> list[str]:
    intent = case.get("intent_expected") or "general_info"
    mapping = {
        "fee_inquiry": ["fee"],
        "processing_time": ["processing_time"],
        "document_list": ["document", "conditional_document"],
        "procedure_inquiry": ["procedure_step", "application_url"],
        "application_url": ["application_url"],
        "eligibility_inquiry": ["eligibility"],
        "general_info": ["other", "office"],
    }
    return mapping.get(intent, ["other"])


def actual_claim_types(actual: dict) -> list[str]:
    types: list[str] = []
    if actual.get("fees"):
        types.append("fee")
    if actual.get("official_urls"):
        types.append("application_url")
    cites = actual.get("citations") or []
    for c in cites:
        ex = (c.get("excerpt") or "").lower()
        if "day" in ex or "din" in ex or "sla" in ex:
            types.append("processing_time")
        if "fee" in ex or "taka" in ex:
            types.append("fee")
    return sorted(set(types))


def classify_outcome(row: dict, case: dict) -> str:
    if row.get("actual_outcome") == "CORRECT_UNCERTAINTY":
        return "CORRECT_UNCERTAINTY"
    if row.get("actual_outcome") == "CORRECT_REFUSAL":
        return "CORRECT_REFUSAL"
    if case.get("expect", {}).get("clarification_ok") and not case.get("service_expected"):
        return "CLARIFICATION_REQUIRED"
    if row.get("pass"):
        return "ANSWER_SUPPORTED"
    if row.get("counts_as_product_failure"):
        return "PRODUCT_FAILURE"
    if case.get("expect", {}).get("uncertainty_ok") and row.get("actual_outcome") == "CORRECT_UNCERTAINTY":
        return "CORRECT_UNCERTAINTY"
    return "EVALUATOR_PROBLEM"


def root_cause(row: dict) -> str | None:
    if row.get("actual_outcome") != "PRODUCT_FAILURE":
        return None
    fc = row.get("failure_class")
    reasons = " | ".join(row.get("reasons") or [])
    if "service mismatch" in reasons:
        return f"service_routing ({fc})"
    if "intent mismatch" in reasons:
        return f"intent_classification ({fc})"
    if "missing official URL" in reasons:
        return "url_retrieval_or_catalogue_reference"
    if "hallucin" in reasons.lower():
        return "hallucination"
    return fc or "unknown"


def main() -> int:
    cases = {c["id"]: c for c in json.loads(QUERIES.read_text(encoding="utf-8"))}
    rows = [json.loads(line) for line in RESULTS.read_text(encoding="utf-8").splitlines() if line.strip()]

    records = []
    counts: dict[str, int] = {}
    product_failures = []

    for row in rows:
        case = cases[row["id"]]
        outcome = classify_outcome(row, case)
        counts[outcome] = counts.get(outcome, 0) + 1
        rec = {
            "id": row["id"],
            "query": row["query"],
            "category": row.get("category"),
            "outcome": outcome,
            "pass": row.get("pass"),
            "counts_as_product_failure": row.get("counts_as_product_failure"),
        }
        if outcome == "PRODUCT_FAILURE":
            rec.update(
                {
                    "query": row["query"],
                    "expected_service": case.get("service_expected"),
                    "actual_service": (row.get("actual") or {}).get("service_slug"),
                    "expected_intent": case.get("intent_expected"),
                    "actual_intent": (row.get("actual") or {}).get("intent"),
                    "expected_claim_types": infer_claim_types(case),
                    "actual_claim_types": actual_claim_types(row.get("actual") or {}),
                    "root_cause": root_cause(row),
                    "reasons": row.get("reasons"),
                    "failure_class": row.get("failure_class"),
                }
            )
            product_failures.append(rec)
        records.append(rec)

    payload = {
        "generated_from": str(RESULTS.relative_to(REPO)),
        "total": len(rows),
        "outcome_counts": counts,
        "product_failure_count": len(product_failures),
        "records": records,
        "product_failures": product_failures,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"outcome_counts": counts, "product_failures": len(product_failures)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
