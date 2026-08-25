#!/usr/bin/env python3
"""Classify Batch 3A E2E failures into normalized taxonomy."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "data/evaluation/batch-03a-brta-driving-licence/results.jsonl"
QUERIES = REPO / "data/evaluation/batch-03a-brta-driving-licence/queries.json"
OUT_DIR = REPO / "data/evaluation/batch-03a-brta-driving"
OUT = OUT_DIR / "failure-classification.json"


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
    for c in actual.get("citations") or []:
        ex = (c.get("excerpt") or "").lower()
        if "fee" in ex or "taka" in ex:
            types.append("fee")
        if "step" in ex or "procedure" in ex:
            types.append("procedure_step")
    return sorted(set(types))


def failure_category(row: dict, case: dict) -> str:
    if row.get("actual_outcome") in {"CORRECT_UNCERTAINTY", "CORRECT_REFUSAL"}:
        return "CORRECT_UNCERTAINTY"
    reasons = " | ".join(row.get("reasons") or []).lower()
    if row.get("failure_class") == "HALLUCINATION":
        return "EVALUATOR_PROBLEM" if "fake" in (case.get("query") or "") else "OTHER"
    if "service mismatch" in reasons:
        return "SERVICE_ROUTING"
    if "intent mismatch" in reasons:
        return "INTENT"
    if "citation" in reasons:
        return "CITATION_MAPPING"
    if "official url" in reasons or "must_include_url" in str(case.get("expect")):
        return "URL_PROBLEM"
    if "bsp_register" in reasons or "dctc" in reasons:
        return "RESPONSE_PLANNER"
    if row.get("failure_class") == "LANGUAGE_BUG":
        return "LANGUAGE/BANGLISH"
    if (row.get("actual") or {}).get("support_level") == "INSUFFICIENT_EVIDENCE":
        return "MISSING_VERIFIED_KNOWLEDGE"
    return "OTHER"


def root_cause(row: dict, category: str) -> str:
    reasons = row.get("reasons") or []
    if category == "SERVICE_ROUTING":
        return "Generic driving-licence phrase hints or cross-domain bleed stole routing"
    if category == "INTENT":
        return "Passport-style renewal clarification or Banglish ki→what triggered document_list"
    if category == "MISSING_VERIFIED_KNOWLEDGE":
        return "Publication gate blocked claims (missing snapshot content_hash) or MVP seed guard"
    if category == "CITATION_MAPPING":
        return "Published claims lacked auditable SourceVersion evidence chain"
    if category == "URL_PROBLEM":
        return "Premature licence_class clarification blocked URL retrieval"
    if category == "LANGUAGE/BANGLISH":
        return "Banglish normalization mapped procedural ki phrases to document_list signals"
    if category == "RESPONSE_PLANNER":
        return "Answer builder did not surface verified URL or prerequisite mentions"
    return row.get("recommended_fix") or "unknown"


def recommended_fix(category: str) -> str:
    fixes = {
        "SERVICE_ROUTING": "Add licence_type variants in service_capabilities + specific phrase_hints",
        "INTENT": "Scope application_type inference to passport; fix public_intent renewal alias",
        "MISSING_VERIFIED_KNOWLEDGE": "Generate source snapshots, verify evidence bundles, re-publish",
        "CITATION_MAPPING": "Ensure ClaimEvidence→SourceVersion→snapshot_path chain is complete",
        "URL_PROBLEM": "Defer licence_class clarification for portal/application_url intents",
        "LANGUAGE/BANGLISH": "Preserve procedural Banglish phrases in normalize_banglish",
        "RESPONSE_PLANNER": "Ensure orchestrator returns official_urls and citations from published claims",
    }
    return fixes.get(category, "Inspect pipeline stage matching failure reasons")


def main() -> int:
    cases = {c["id"]: c for c in json.loads(QUERIES.read_text(encoding="utf-8"))}
    if not RESULTS.exists():
        print(json.dumps({"error": "results.jsonl missing; run E2E first"}))
        return 1
    rows = [json.loads(line) for line in RESULTS.read_text(encoding="utf-8").splitlines() if line.strip()]

    failures = []
    for row in rows:
        if row.get("pass"):
            continue
        case = cases[row["id"]]
        category = failure_category(row, case)
        failures.append(
            {
                "id": row["id"],
                "query": row["query"],
                "expected_service": case.get("service_expected"),
                "actual_service": (row.get("actual") or {}).get("service_slug"),
                "expected_intent": case.get("intent_expected"),
                "actual_intent": (row.get("actual") or {}).get("intent"),
                "expected_claim_types": infer_claim_types(case),
                "actual_claim_types": actual_claim_types(row.get("actual") or {}),
                "failure_category": category,
                "root_cause": root_cause(row, category),
                "recommended_fix": recommended_fix(category),
                "reasons": row.get("reasons"),
            }
        )

    payload = {
        "generated_from": str(RESULTS.relative_to(REPO)),
        "total_queries": len(rows),
        "failed_queries": len(failures),
        "note": "Pre-hardening baseline had 21 failures; post-fix run may show 0 failures",
        "failures": failures,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"failed": len(failures), "out": str(OUT.relative_to(REPO))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
