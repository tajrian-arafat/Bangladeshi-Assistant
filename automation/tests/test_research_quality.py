"""Tests for service-specific research quality model."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.orchestrator.research_quality import (
    classify_claim,
    evaluate_service_research,
    load_profiles,
    resolve_profile_key,
    source_is_service_specific,
)
from automation.orchestrator.service_research_builder import PILOT_SERVICE_IDS, ServiceResearchBuilder
from automation.orchestrator.phase_completion import check_research_complete, check_batch_research_quality

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture()
def profiles_doc() -> dict:
    return load_profiles(REPO)


def test_boilerplate_claim_classified_as_catalogue_metadata(profiles_doc: dict) -> None:
    claim = {
        "claim_id": "land-deed-registration::c-application-portal",
        "service_id": "land-deed-registration",
        "claim_type": "application_url",
        "claim_text": "Deed Registration is associated with NBR e-service portal https://nbr.gov.bd/",
        "source_ids": ["src-catalogue"],
    }
    entry = {"service_id": "land-deed-registration", "category_id": "land", "authority_id": "land_ministry"}
    result = classify_claim(claim, catalogue_entry=entry, profiles_doc=profiles_doc)
    assert result.claim_class == "CATALOGUE_METADATA"
    assert not result.meaningful


def test_service_specific_claim_recognized(profiles_doc: dict) -> None:
    claim = {
        "claim_id": "land-deed-registration::c-procedure",
        "service_id": "land-deed-registration",
        "claim_type": "procedure_step",
        "claim_text": "Deed registration is processed at the Sub-Registry Office under the Department of Registration.",
        "source_ids": ["src-land-official"],
    }
    sources = {"src-land-official": {"source_id": "src-land-official", "url": "https://www.land.gov.bd/poripotro", "tier": 1, "service_id": "land-deed-registration"}}
    entry = {"service_id": "land-deed-registration", "category_id": "land", "authority_id": "land_ministry", "service_name_en": "Deed Registration"}
    result = classify_claim(claim, catalogue_entry=entry, sources_by_id=sources, profiles_doc=profiles_doc)
    assert result.claim_class == "SERVICE_SPECIFIC"
    assert result.meaningful


def test_nbr_domain_forbidden_for_land(profiles_doc: dict) -> None:
    entry = {"service_id": "land-deed-registration", "category_id": "land", "authority_id": "land_ministry"}
    source = {"source_id": "src-bad", "url": "https://nbr.gov.bd/all-eservices/eng", "tier": 1, "service_id": "land-deed-registration"}
    assert not source_is_service_specific(source, entry, profiles_doc)


def test_resolve_profile_key_land(profiles_doc: dict) -> None:
    entry = {"category_id": "land", "authority_id": "land_ministry"}
    assert resolve_profile_key(entry, profiles_doc) == "LAND"


def test_generic_builder_batch_has_false_completion(batch04: dict) -> None:
    from automation.orchestrator.research_quality import evaluate_batch_research_quality

    quality = evaluate_batch_research_quality(REPO, batch04)
    assert quality.false_completion_count > 0
    assert not quality.complete


def test_pilot_service_research_produces_meaningful_claims() -> None:
    builder = ServiceResearchBuilder(REPO)
    result = builder.build_service_research("land-deed-registration")
    assert result["meaningful_claims"] >= 2
    assert result["service_specific_sources"] >= 1
    pilot_path = REPO / "data" / "research" / "pilot" / "land-deed-registration" / "service.json"
    assert pilot_path.exists()


def test_pilot_service_ids_count() -> None:
    assert len(PILOT_SERVICE_IDS) == 10


@pytest.fixture()
def batch04() -> dict:
    queue = json.loads((REPO / ".automation" / "batch_queue.json").read_text(encoding="utf-8"))
    return next(b for b in queue["batches"] if b["batch_id"] == "BATCH_04")


def test_check_research_complete_blocks_scaffolding(batch04: dict) -> None:
    report = check_research_complete(REPO, batch04)
    assert not report.complete
    assert any("scaffolding" in m.lower() or "false_completion" in m.lower() for m in report.missing)
