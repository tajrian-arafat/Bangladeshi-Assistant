"""Batch 3B gap-closure artifact and orchestrator transition tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GAP = REPO / "data/research/verification/batch-03b-brta-vehicle-gap-closure"
VERIFY = REPO / "data/research/verification/batch-03b-brta-vehicle"
STAGING = REPO / "data/research/staging/batch-03b-brta-vehicle"


def test_gap_closure_generator_produces_artifacts() -> None:
    subprocess.run(
        ["python3", "scripts/generate_batch03b_brta_vehicle_gap_closure.py"],
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
    bsp = next(t for t in scrape["targets"] if t["id"] == "bsp_vehicle_registration")
    assert bsp["http_status"] == 404
    assert bsp["availability"] == "TEMPORARILY_UNAVAILABLE"
    brta = next(t for t in scrape["targets"] if t["id"] == "brta_ownership_transfer")
    assert brta["http_status"] == 200
    assert brta["availability"] == "RENDERED"


def test_calculator_derived_fee_claim_not_static() -> None:
    claims = json.loads((GAP / "new_claims.json").read_text(encoding="utf-8"))["claims"]
    fee_claim = next(c for c in claims if c["claim_id"] == "gap-closure::c-vehicle-fees-calculator-derived")
    assert fee_claim["structured_value"]["amount"] == "CALCULATOR_DERIVED"
    assert fee_claim["verification_status"] == "PARTIALLY_VERIFIED"


def test_deferred_cross_batch_fitness_gap() -> None:
    deps = json.loads((GAP / "cross_batch_dependencies.json").read_text(encoding="utf-8"))["dependencies"]
    assert any(d["to_batch"] == "BATCH_03C" for d in deps)
    gaps = json.loads((GAP / "knowledge_gaps.json").read_text(encoding="utf-8"))["knowledge_gaps"]
    fitness = next(g for g in gaps if g["gap_id"] == "MISSING_FITNESS_VALIDITY_BY_CLASS")
    assert fitness["status"] == "DEFERRED"


def test_verify_merges_gap_closure_claims() -> None:
    subprocess.run(["python3", "scripts/verify_batch03b_brta_vehicle_claims.py"], cwd=REPO, check=True)
    data = json.loads((VERIFY / "claims_verification.json").read_text(encoding="utf-8"))
    ids = {c["claim_id"] for c in data["claims"]}
    assert "gap-closure::c-bsp-subportals-temporarily-unavailable" in ids
    summary = json.loads((VERIFY / "summary.json").read_text(encoding="utf-8"))
    assert summary["knowledge_gaps"] == 0
    assert summary["gap_closure_claims"] >= 7


def test_normalize_staging_supersession_and_calculator_fee() -> None:
    subprocess.run(["python3", "scripts/normalize_batch03b_brta_vehicle_to_staging.py"], cwd=REPO, check=True)
    manifest = json.loads((STAGING / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["gap_closure_claims"] >= 7
    claims = json.loads((STAGING / "claims.json").read_text(encoding="utf-8"))["claims"]
    portal = next(c for c in claims if c["claim_id"] == "brta-new-vehicle-registration::c-portal-url")
    assert portal["superseded_by_claim_key"] == "gap-closure::c-bsp-subportals-temporarily-unavailable"
    fees = json.loads((STAGING / "fees.json").read_text(encoding="utf-8"))["fees"]
    assert fees and fees[0]["amount"] == "CALCULATOR_DERIVED"


def test_gap_closure_to_publication_transition() -> None:
    from automation.orchestrator.phase_executor import PhaseExecutor

    executor = PhaseExecutor(REPO)
    batch = {"batch_id": "BATCH_03B", "slug": "batch-03b-brta-vehicle"}
    result = executor.execute_gap_closure(run_id="run-test-gap", batch=batch)
    assert result.phase == "GAP_CLOSURE"
    assert result.status == "SUCCESS"
    assert result.recommended_next_phase == "PUBLICATION"
