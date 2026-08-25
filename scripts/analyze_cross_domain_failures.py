#!/usr/bin/env python3
"""Analyze Batch 2B product failures for cross-domain root-cause taxonomy."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLASSIFICATION = REPO / "data/evaluation/batch-02b-police-immigration/failure-classification.json"
OUT = REPO / "data/evaluation/cross-domain-failure-analysis.json"

# Pre-hardening baseline (Step 20 stabilization)
BASELINE = {
    "normalized_pass_pct": 77.6,
    "product_failure_count": 15,
    "product_failure_ids": [
        "b009", "b014", "b018", "b022", "b023", "b025", "b027", "b029",
        "b033", "b038", "b046", "b050", "b055", "b059", "b062",
    ],
}

MECHANISM_MAP = {
    "LANGUAGE_BUG": {
        "mechanism": "language_normalization + intent_classification",
        "domains": ["police", "immigration", "passport"],
    },
    "RETRIEVAL_BUG": {
        "mechanism": "service_candidate_scoring + context_resolution + capability_matching",
        "domains": ["police", "immigration", "passport", "transport"],
    },
    "OTHER": {
        "mechanism": "intent_classification",
        "domains": ["police", "immigration"],
    },
}

ROOT_CAUSE_DETAIL = {
    "b009": {
        "root_cause": "kothay/where mapped to office_locator instead of application_url for visa apply queries",
        "reusable_mechanism": "semantic_phrases.application_location + intent tie-break",
        "layer": "intent_classification",
    },
    "b014": {
        "root_cause": "koto din valid conflated with processing_time; bare koto triggered fee alias",
        "reusable_mechanism": "validity_inquiry semantic group + banglish validity normalization",
        "layer": "language_normalization",
    },
    "b018": {
        "root_cause": "follow-up online channel lost PCC service context; routed to passport",
        "reusable_mechanism": "context_resolution + clarification channel inheritance",
        "layer": "context_resolution",
    },
    "b022": {
        "root_cause": "Bangla কত দিন লাগে not detected as processing_time on raw text",
        "reusable_mechanism": "semantic_phrases time_inquiry on raw_message",
        "layer": "language_normalization",
    },
    "b023": {
        "root_cause": "GD document query had no service candidate match",
        "reusable_mechanism": "phrase_hints + capability profiles for GD online",
        "layer": "capability_matching",
    },
    "b025": {
        "root_cause": "lost mobile GD filed as document_list instead of procedure_inquiry",
        "reusable_mechanism": "GD online lost-item procedure disambiguation",
        "layer": "intent_classification",
    },
    "b027": {
        "root_cause": "explicit url request downgraded to procedure_inquiry via public_intent",
        "reusable_mechanism": "public_intent preserves application_url",
        "layer": "response_planning",
    },
    "b029": {
        "root_cause": "urgent passport verification SLA routed to epassport-urgent-super-express",
        "reusable_mechanism": "service_bleed guard: domain + verification context before speed variant",
        "layer": "service_candidate_scoring",
    },
    "b033": {
        "root_cause": "comparison query routed to PCC instead of passport verification",
        "reusable_mechanism": "comparison intent + PV vs PCC bleed guard",
        "layer": "service_candidate_scoring",
    },
    "b038": {
        "root_cause": "responsible-for overview classified as document_list",
        "reusable_mechanism": "semantic_phrases.overview → general_info",
        "layer": "intent_classification",
    },
    "b046": {
        "root_cause": "business visa query missed immigration service match",
        "reusable_mechanism": "visa_types phrase hints + immigration domain filter",
        "layer": "capability_matching",
    },
    "b050": {
        "root_cause": "expatriate cell overview classified as document_list",
        "reusable_mechanism": "semantic_phrases.overview → general_info",
        "layer": "intent_classification",
    },
    "b055": {
        "root_cause": "AIG responsibility query classified as document_list",
        "reusable_mechanism": "semantic_phrases.overview → general_info",
        "layer": "intent_classification",
    },
    "b059": {
        "root_cause": "firearms license documents routed to driving-licence-renewal via generic license token",
        "reusable_mechanism": "firearms domain + licence family disambiguation",
        "layer": "service_candidate_scoring",
    },
    "b062": {
        "root_cause": "online nationwide GD query routed to offline GD service",
        "reusable_mechanism": "online channel variant scoring for GD family",
        "layer": "service_candidate_scoring",
    },
}


def classify_layer(failure_class: str | None, detail: dict) -> str:
    return detail.get("layer") or MECHANISM_MAP.get(failure_class or "", {}).get(
        "mechanism", "unknown"
    )


def main() -> int:
    src = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    records = []
    for pf in src.get("product_failures", []):
        fid = pf["id"]
        detail = ROOT_CAUSE_DETAIL.get(fid, {})
        fc = pf.get("failure_class")
        records.append(
            {
                "id": fid,
                "query": pf.get("query"),
                "category": pf.get("category"),
                "failure_class": fc,
                "root_cause": detail.get("root_cause") or pf.get("root_cause"),
                "reusable_mechanism": detail.get("reusable_mechanism"),
                "affected_domains": MECHANISM_MAP.get(fc or "", {}).get("domains", []),
                "problem_layer": classify_layer(fc, detail),
                "evaluator_error": False,
                "expected": {
                    "service": pf.get("expected_service"),
                    "intent": pf.get("expected_intent"),
                },
                "actual_at_baseline": {
                    "service": pf.get("actual_service"),
                    "intent": pf.get("actual_intent"),
                },
            }
        )

    payload = {
        "generated_from": str(CLASSIFICATION.relative_to(REPO)),
        "baseline": BASELINE,
        "step21_fixes": [
            "backend/app/ai/routing/semantic_phrases.py",
            "backend/app/ai/routing/context_resolution.py",
            "backend/app/ai/pipeline/banglish.py",
            "backend/app/ai/routing/intent_classifier.py",
            "backend/app/ai/routing/intent_canonical.py",
            "backend/app/ai/routing/domain_entities.py",
            "backend/app/ai/routing/service_router.py",
            "backend/app/application/services/conversation_context.py",
            "backend/app/ai/orchestrator.py",
            "data/routing/capability_aliases.json",
            "data/routing/intent_taxonomy.json",
            "data/routing/phrase_hints.json",
        ],
        "records": records,
        "summary_by_layer": {},
    }
    layers: dict[str, int] = {}
    for r in records:
        layers[r["problem_layer"]] = layers.get(r["problem_layer"], 0) + 1
    payload["summary_by_layer"] = layers

    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "layers": layers}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
