"""Tests for deep-research pilot builder."""

from __future__ import annotations

from pathlib import Path

from automation.orchestrator.deep_research_builder import DEEP_SERVICE_HINTS, DeepResearchBuilder

REPO = Path(__file__).resolve().parents[2]


def test_deep_hints_cover_pilot_services() -> None:
    assert len(DEEP_SERVICE_HINTS) >= 12


def test_deep_research_produces_artifacts() -> None:
    builder = DeepResearchBuilder(REPO)
    service_id = "land-mutation-apply"
    result = builder.build_deep_research(service_id)
    out_dir = Path(result["output_dir"])
    assert (out_dir / "service.json").exists()
    assert (out_dir / "claims.json").exists()
    assert result["after_meaningful_claims"] >= result["before_meaningful_claims"]


def test_deep_e2e_has_twelve_queries() -> None:
    builder = DeepResearchBuilder(REPO)
    service_id = "land-mutation-apply"
    builder.build_deep_research(service_id)
    verification = builder.verify_deep_claims(service_id)
    e2e = builder.run_deep_e2e(service_id, verification["verification_map"])
    assert e2e["total"] >= 12
