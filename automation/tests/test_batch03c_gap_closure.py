"""Batch 3C gap-closure artifact and orchestrator transition tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GAP = REPO / "data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure"
VERIFY = REPO / "data/research/verification/batch-03c-brta-fitness-tax-permit"
STAGING = REPO / "data/research/staging/batch-03c-brta-fitness-tax-permit"
QUERIES = REPO / "data/evaluation/batch-03c-brta-fitness-tax-permit/queries.json"


def test_queries_json_has_55_cases() -> None:
    cases = json.loads(QUERIES.read_text(encoding="utf-8"))
    assert len(cases) == 55
    ids = {c["id"] for c in cases}
    assert len(ids) == 55
    validity_cases = [c for c in cases if c.get("category") == "FITNESS_VALIDITY"]
    assert len(validity_cases) >= 3
    assert all(c["expect"].get("must_not_affirm_validity") for c in validity_cases)


def test_eval_outcomes_rejects_five_year_validity_affirmation() -> None:
    from scripts.batch03c_eval_outcomes import evaluate_batch03c_outcome

    case = {
        "category": "FITNESS_VALIDITY",
        "service_expected": "brta-fitness-certificate",
        "expect": {"must_not_affirm_validity": True, "must_reject_years": "5", "uncertainty_ok": True},
    }
    bad = {
        "service_slug": "brta-fitness-certificate",
        "summary": "Private car fitness certificate is valid for 5 years.",
        "warnings": [],
        "fees": [],
        "citations": [],
        "official_urls": [],
    }
    good = {
        "service_slug": "brta-fitness-certificate",
        "summary": "Fitness validity by vehicle class is not verified; periods vary and are not confirmed.",
        "warnings": [],
        "fees": [],
        "citations": [],
        "official_urls": [],
    }
    bad_out = evaluate_batch03c_outcome(case, bad, {"reasons": [], "checks": {}})
    good_out = evaluate_batch03c_outcome(case, good, {"reasons": [], "checks": {}})
    assert bad_out["actual_outcome"] == "PRODUCT_FAILURE"
    assert good_out["pass"] is True


def test_eval_outcomes_route_permit_alternate_routing() -> None:
    from scripts.batch03c_eval_outcomes import evaluate_batch03c_outcome

    case = {
        "category": "ROUTE_PERMIT",
        "service_expected": "brta-route-permit",
        "expect": {"allow_route_permit_alternates": True},
    }
    actual = {
        "service_slug": "transport-route-permit",
        "summary": "Route permit BSP operator service.",
        "warnings": [],
        "fees": [],
        "citations": [],
        "official_urls": [],
    }
    out = evaluate_batch03c_outcome(case, actual, {"reasons": ["service mismatch"], "checks": {"service": False}})
    assert out["checks"].get("service") is True


def test_gap_closure_generator_produces_artifacts() -> None:
    subprocess.run(
        ["python3", "scripts/generate_batch03c_brta_fitness_tax_permit_gap_closure.py"],
        cwd=REPO,
        check=True,
    )
    assert (GAP / "new_claims.json").exists()
    assert (GAP / "knowledge_gaps.json").exists()
    assert (GAP / "cross_batch_dependencies.json").exists()
    assert (GAP / "supersessions.json").exists()
    summary = json.loads((GAP / "summary.json").read_text(encoding="utf-8"))
    assert summary["knowledge_gaps"] == 0
    assert summary["new_claims"] >= 7


def test_browser_snapshot_availability_classification() -> None:
    scrape = json.loads((GAP / "source_snapshots/scrape_results.json").read_text(encoding="utf-8"))
    fitness = next(t for t in scrape["targets"] if t["id"] == "brta_fitness")
    assert fitness["http_status"] == 200
    assert fitness["availability"] == "RENDERED"
    tax = next(t for t in scrape["targets"] if t["id"] == "brta_tax_token")
    assert tax["http_status"] == 200
    assert tax["availability"] == "RENDERED"
    route = next(t for t in scrape["targets"] if t["id"] == "bsp_fee_calculator")
    assert route["availability"] in {"RENDERED", "TEMPORARILY_UNAVAILABLE"}


def test_calculator_derived_fee_claim_not_static() -> None:
    claims = json.loads((GAP / "new_claims.json").read_text(encoding="utf-8"))["claims"]
    fee_claim = next(c for c in claims if c["claim_id"] == "gap-closure::c-fitness-tax-fees-calculator-derived")
    assert fee_claim["structured_value"]["amount"] == "CALCULATOR_DERIVED"
    assert fee_claim["verification_status"] == "PARTIALLY_VERIFIED"


def test_fitness_validity_gap_open_in_batch03c() -> None:
    gaps = json.loads((GAP / "knowledge_gaps.json").read_text(encoding="utf-8"))["knowledge_gaps"]
    fitness = next(g for g in gaps if g["gap_id"] == "MISSING_FITNESS_VALIDITY_BY_CLASS")
    assert fitness["status"] == "OPEN"
    deps = json.loads((GAP / "cross_batch_dependencies.json").read_text(encoding="utf-8"))["dependencies"]
    assert any(d["from_batch"] == "BATCH_03B" for d in deps)


def test_verify_merges_gap_closure_claims() -> None:
    subprocess.run(["python3", "scripts/verify_batch03c_brta_fitness_tax_permit_claims.py"], cwd=REPO, check=True)
    data = json.loads((VERIFY / "claims_verification.json").read_text(encoding="utf-8"))
    ids = {c["claim_id"] for c in data["claims"]}
    assert "gap-closure::c-fitness-tax-fees-calculator-derived" in ids
    summary = json.loads((VERIFY / "summary.json").read_text(encoding="utf-8"))
    assert summary["knowledge_gaps"] == 0
    assert summary["gap_closure_claims"] >= 7


def test_normalize_staging_supersession_and_calculator_fee() -> None:
    subprocess.run(["python3", "scripts/normalize_batch03c_brta_fitness_tax_permit_to_staging.py"], cwd=REPO, check=True)
    manifest = json.loads((STAGING / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["gap_closure_claims"] >= 7
    claims = json.loads((STAGING / "claims.json").read_text(encoding="utf-8"))["claims"]
    portal = next(c for c in claims if c["claim_id"] == "brta-fitness-certificate::c-validity-by-class-unverified")
    assert portal["provenance"]["verification_status"] == "UNVERIFIED"
    fees = json.loads((STAGING / "fees.json").read_text(encoding="utf-8"))["fees"]
    assert fees and fees[0]["amount"] == "CALCULATOR_DERIVED"


def test_gap_closure_to_publication_transition() -> None:
    from automation.orchestrator.phase_executor import PhaseExecutor

    executor = PhaseExecutor(REPO)
    batch = {"batch_id": "BATCH_03C", "slug": "batch-03c-brta-fitness-tax-permit"}
    result = executor.execute_gap_closure(run_id="run-test-gap-03c", batch=batch)
    assert result.phase == "GAP_CLOSURE"
    assert result.status == "SUCCESS"
    assert result.recommended_next_phase == "PUBLICATION"
