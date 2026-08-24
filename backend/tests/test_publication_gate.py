"""Publication gate and claim publish safety tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.knowledge.publication_gate import (
    assert_mapping_safe,
    can_populate_fee,
    can_populate_must_need,
    evaluate_official_publication,
)
from app.application.knowledge.publisher import KnowledgePublisher, MVP_SEED_SLUGS
from app.core.exceptions import ValidationError
from app.domain.enums import (
    ClaimPipelineStatus,
    ClaimType,
    InformationClass,
)
from app.domain.models.claims import Claim, ClaimEvidence
from app.domain.models.knowledge import Agency, Fee, Service, Source, SourceVersion
from pathlib import Path


def _base_gate_kwargs(**overrides):
    data = {
        "pipeline_status": ClaimPipelineStatus.VERIFIED.value,
        "information_class": InformationClass.OFFICIAL.value,
        "claim_type": ClaimType.FEE.value,
        "evidence": [{"evidence_excerpt": "Fee is 50 BDT", "locator": None}],
        "authority_tiers": [1],
        "has_unresolved_conflict": False,
        "verified_at": datetime.now(timezone.utc),
        "reviewer_approved": True,
        "provenance_complete": True,
        "content_hash_present": True,
        "retrieved_at": datetime.now(timezone.utc),
    }
    data.update(overrides)
    return data


def test_unverified_claim_cannot_publish():
    gate = evaluate_official_publication(
        **_base_gate_kwargs(pipeline_status=ClaimPipelineStatus.CROSS_CHECKED.value)
    )
    assert not gate.allowed
    assert any("VERIFIED" in r for r in gate.reasons)


def test_conflicting_claim_cannot_publish():
    gate = evaluate_official_publication(**_base_gate_kwargs(has_unresolved_conflict=True))
    assert not gate.allowed
    assert any("conflict" in r.lower() for r in gate.reasons)


def test_practical_claim_cannot_populate_must_need():
    gate = evaluate_official_publication(**_base_gate_kwargs())
    must = can_populate_must_need(
        information_class=InformationClass.PRACTICAL.value,
        pipeline_status=ClaimPipelineStatus.VERIFIED.value,
        gate=gate,
    )
    assert not must.allowed
    assert any("MUST NEED" in r or "PRACTICAL" in r for r in must.reasons)


def test_fee_without_evidence_cannot_publish():
    gate = evaluate_official_publication(**_base_gate_kwargs(evidence=[]))
    fee = can_populate_fee(
        gate=gate,
        information_class=InformationClass.OFFICIAL.value,
        claim_type=ClaimType.FEE.value,
    )
    assert not fee.allowed


def test_procedure_without_evidence_cannot_publish():
    gate = evaluate_official_publication(
        **_base_gate_kwargs(
            claim_type=ClaimType.PROCEDURE_STEP.value,
            evidence=[],
        )
    )
    assert not gate.allowed


def test_verified_claim_can_publish():
    gate = evaluate_official_publication(**_base_gate_kwargs())
    assert gate.allowed
    fee = can_populate_fee(
        gate=gate,
        information_class=InformationClass.OFFICIAL.value,
        claim_type=ClaimType.FEE.value,
    )
    assert fee.allowed


def test_source_provenance_trace_requires_complete_chain():
    gate = evaluate_official_publication(**_base_gate_kwargs(provenance_complete=False))
    assert not gate.allowed
    assert any("provenance" in r.lower() for r in gate.reasons)


def test_service_mapping_cannot_target_wrong_service():
    gate = assert_mapping_safe(
        catalogue_service_id="civil-birth-registration",
        expected_runtime_slug="birth-registration",
        actual_runtime_slug="nid-correction",
        mapping_review_status="APPROVED",
        allow_overwrite_seed=True,
        target_is_mvp_seed=True,
    )
    assert not gate.allowed
    assert any("wrong service" in r for r in gate.reasons)


def test_mvp_seed_not_silently_overwritten():
    gate = assert_mapping_safe(
        catalogue_service_id="civil-birth-registration",
        expected_runtime_slug="birth-registration",
        actual_runtime_slug="birth-registration",
        mapping_review_status="NEEDS_REVIEW",
        allow_overwrite_seed=False,
        target_is_mvp_seed=True,
    )
    assert not gate.allowed
    assert any("MVP seed" in r for r in gate.reasons)


@pytest_asyncio.fixture
async def agency_service(test_session: AsyncSession):
    agency = Agency(
        slug="test-agency",
        name_bn="টেস্ট",
        name_en="Test Agency",
    )
    test_session.add(agency)
    await test_session.flush()
    service = Service(
        slug="birth-registration",
        name_bn="জন্ম নিবন্ধন",
        name_en="Birth Registration",
        agency_id=agency.id,
        category="CIVIL_REGISTRATION",
        status="UNDER_REVIEW",
        review_state="DRAFT",
    )
    test_session.add(service)
    await test_session.flush()
    return agency, service


@pytest.mark.asyncio
async def test_mvp_seed_blocks_structured_fee_publish(test_session: AsyncSession, agency_service, tmp_path):
    """MVP seed structured overwrites are skipped; publish completes without error."""
    _, service = agency_service
    service_id = service.id
    assert service.slug in MVP_SEED_SLUGS

    source = Source(domain="example.gov.bd", title="Example", tier=1)
    test_session.add(source)
    await test_session.flush()
    sv = SourceVersion(
        source_id=source.id,
        url="https://example.gov.bd/fees",
        content_hash="abc123",
        retrieved_at=datetime.now(timezone.utc),
        raw_content_path=None,
    )
    test_session.add(sv)
    await test_session.flush()

    claim = Claim(
        service_id=service_id,
        research_claim_key="test::fee",
        claim_type=ClaimType.FEE.value,
        subject="Late fee",
        predicate="is",
        value="50 BDT",
        structured_value={"amount": "50", "currency": "BDT"},
        information_class=InformationClass.OFFICIAL.value,
        pipeline_status=ClaimPipelineStatus.VERIFIED.value,
        verified_at=datetime.now(timezone.utc),
        confidence=0.9,
    )
    test_session.add(claim)
    await test_session.flush()
    test_session.add(
        ClaimEvidence(
            claim_id=claim.id,
            source_version_id=sv.id,
            evidence_excerpt="Fee is 50 BDT",
            evidence_strength="STRONG",
        )
    )
    await test_session.commit()

    staging = tmp_path / "data" / "research" / "staging" / "batch-01"
    staging.mkdir(parents=True)
    (staging / "services.json").write_text(
        '{"services":[{"service_id":"civil-birth-registration"}]}', encoding="utf-8"
    )
    (staging / "fees.json").write_text('{"fees":[]}', encoding="utf-8")
    mapping_path = tmp_path / "data" / "research" / "catalogue_runtime_mappings.json"
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.write_text(
        """{
          "mappings": [{
            "catalogue_service_id": "civil-birth-registration",
            "runtime_slug": "birth-registration",
            "mapping_type": "existing_seed",
            "review_status": "NEEDS_REVIEW",
            "allow_overwrite_seed": false
          }]
        }""",
        encoding="utf-8",
    )
    vdir = tmp_path / "data" / "research" / "verification" / "batch-01"
    vdir.mkdir(parents=True)
    (vdir / "claims_verification.json").write_text(
        json.dumps({"claims": []}),
        encoding="utf-8",
    )

    publisher = KnowledgePublisher(test_session, repo_root=tmp_path, dry_run=False)
    report = await publisher.publish_verified("batch-01")
    assert report.ok
    assert any(a.get("action") == "skip_mvp_seed_fee_overwrite" for a in report.actions)

    from sqlalchemy import select

    fees = (
        await test_session.execute(select(Fee).where(Fee.service_id == service_id))
    ).scalars().all()
    assert fees == []
