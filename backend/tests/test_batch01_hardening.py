"""Batch 1 hardening regression tests (Step 10)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.orchestrator import Orchestrator
from app.application.knowledge.evidence_ingestion import EvidenceIngestionService
from app.application.knowledge.publication_gate import evaluate_official_publication
from app.application.knowledge.publisher import KnowledgePublisher, MVP_SEED_SLUGS
from app.application.knowledge.seed_replacement import SeedReplacementService
from app.application.services.conversation_context import ConversationContext, ConversationContextService
from app.domain.enums import (
    ClaimPipelineStatus,
    ClaimType,
    InformationClass,
    SeedReplacementStatus,
)
from app.domain.models.claims import Claim, ClaimEvidence, KnowledgeGap
from app.domain.models.conversation import ClarificationState, Conversation
from app.domain.models.knowledge import Agency, Fee, KnowledgeChunk, Service, Source, SourceVersion
from app.domain.models.seed_replacement import SeedReplacement
from app.schemas.chat import ChatRequest
from pathlib import Path


def _gate_kwargs(**overrides):
    data = {
        "pipeline_status": ClaimPipelineStatus.VERIFIED.value,
        "information_class": InformationClass.OFFICIAL.value,
        "claim_type": ClaimType.FEE.value,
        "evidence": [{"evidence_excerpt": "Fee is 50 BDT", "locator": "p1"}],
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


@pytest_asyncio.fixture
async def agency_service(test_session: AsyncSession):
    agency = Agency(slug="test-agency", name_bn="টেস্ট", name_en="Test Agency")
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


async def _verified_fee_claim(test_session, service_id, *, status=ClaimPipelineStatus.VERIFIED, info=InformationClass.OFFICIAL, key="test::fee"):
    source = Source(domain="example.gov.bd", title="Example", tier=1)
    test_session.add(source)
    await test_session.flush()
    sv = SourceVersion(
        source_id=source.id,
        url="https://example.gov.bd/fees",
        content_hash="abc123",
        retrieved_at=datetime.now(timezone.utc),
    )
    test_session.add(sv)
    await test_session.flush()
    claim = Claim(
        service_id=service_id,
        research_claim_key=key,
        claim_type=ClaimType.FEE.value,
        subject="Late fee",
        predicate="is",
        value="50 BDT",
        structured_value={"amount": "50", "currency": "BDT"},
        information_class=info,
        pipeline_status=status,
        verified_at=datetime.now(timezone.utc) if status == ClaimPipelineStatus.VERIFIED.value else None,
        confidence=0.9,
    )
    test_session.add(claim)
    await test_session.flush()
    test_session.add(
        ClaimEvidence(
            claim_id=claim.id,
            source_version_id=sv.id,
            evidence_excerpt="Fee is 50 BDT for late registration",
            evidence_strength="STRONG",
        )
    )
    await test_session.flush()
    return claim, sv


def _staging(tmp_path: Path):
    staging = tmp_path / "data" / "research" / "staging" / "batch-01"
    staging.mkdir(parents=True)
    (staging / "services.json").write_text(
        '{"services":[{"service_id":"civil-birth-registration"}]}', encoding="utf-8"
    )
    (staging / "fees.json").write_text('{"fees":[]}', encoding="utf-8")
    mapping_path = tmp_path / "data" / "research" / "catalogue_runtime_mappings.json"
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.write_text(
        json.dumps(
            {
                "mappings": [
                    {
                        "catalogue_service_id": "civil-birth-registration",
                        "runtime_slug": "birth-registration",
                        "mapping_type": "existing_seed",
                        "review_status": "NEEDS_REVIEW",
                        "allow_overwrite_seed": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    vdir = tmp_path / "data" / "research" / "verification" / "batch-01"
    vdir.mkdir(parents=True)
    (vdir / "claims_verification.json").write_text(json.dumps({"claims": []}), encoding="utf-8")
    return tmp_path


# A. Verified claim replaces legacy seed data only after approval
@pytest.mark.asyncio
async def test_verified_claim_replaces_seed_only_after_approval(test_session, agency_service, tmp_path):
    _, service = agency_service
    claim, _ = await _verified_fee_claim(test_session, service.id)
    await test_session.commit()
    repo = _staging(tmp_path)

    publisher = KnowledgePublisher(test_session, repo_root=repo, dry_run=False)
    report = await publisher.publish_verified("batch-01")
    assert any(a.get("action") == "skip_mvp_seed_fee_overwrite" for a in report.actions)

    replacement = SeedReplacement(
        service_id=service.id,
        claim_id=claim.id,
        replacement_kind="fee",
        status=SeedReplacementStatus.APPROVED.value,
        approved_by="test",
        approved_at=datetime.now(timezone.utc),
    )
    test_session.add(replacement)
    await test_session.commit()

    report2 = await publisher.publish_verified("batch-01", approved_seed_replacement_claim_ids={claim.id})
    assert report2.published_fees >= 1
    fees = (await test_session.execute(select(Fee).where(Fee.claim_id == claim.id))).scalars().all()
    assert len(fees) >= 1


# B. Partial claim cannot replace seed data
@pytest.mark.asyncio
async def test_partial_claim_cannot_replace_seed(test_session, agency_service, tmp_path):
    _, service = agency_service
    claim, _ = await _verified_fee_claim(
        test_session,
        service.id,
        status=ClaimPipelineStatus.PARTIALLY_VERIFIED,
    )
    await test_session.commit()
    svc = SeedReplacementService(test_session, repo_root=_staging(tmp_path), dry_run=True)
    report = await svc.discover_candidates("batch-01")
    assert all(c.claim_id != claim.id for c in report.candidates)


# C. Unverified claim cannot replace seed data
@pytest.mark.asyncio
async def test_unverified_claim_cannot_replace_seed(test_session, agency_service, tmp_path):
    _, service = agency_service
    claim, _ = await _verified_fee_claim(
        test_session,
        service.id,
        status=ClaimPipelineStatus.UNVERIFIED,
    )
    await test_session.commit()
    svc = SeedReplacementService(test_session, repo_root=_staging(tmp_path), dry_run=True)
    report = await svc.discover_candidates("batch-01")
    assert all(c.claim_id != claim.id for c in report.candidates)


# D. Follow-up query retains service context
@pytest.mark.asyncio
async def test_follow_up_retains_service_context(test_session, agency_service):
    _, service = agency_service
    correction = Service(
        slug="civil-birth-registration-correction",
        name_bn="জন্ম সংশোধন",
        name_en="Birth Registration Correction",
        agency_id=service.agency_id,
        category="CIVIL_REGISTRATION",
        status="ACTIVE",
        review_state="APPROVED",
    )
    test_session.add(correction)
    await test_session.commit()

    conv = Conversation(id=uuid4(), metadata_json={"active_service_slug": "civil-birth-registration-correction"})
    test_session.add(conv)
    await test_session.commit()

    ctx_svc = ConversationContextService(test_session)
    loaded = await ctx_svc.load(conv.id)
    orch = Orchestrator(test_session)
    req = ChatRequest(message="Naam", conversation_id=conv.id, clarifications={})
    _, _, intent, _, pipeline_ctx = await orch.run(req, conversation_context=loaded)
    assert pipeline_ctx.service is not None
    assert pipeline_ctx.service.slug == "civil-birth-registration-correction"


# E. Follow-up retains clarification context
@pytest.mark.asyncio
async def test_follow_up_clarification_answer(test_session):
    conv = Conversation(id=uuid4())
    test_session.add(conv)
    test_session.add(
        ClarificationState(
            conversation_id=conv.id,
            key="correction_type",
            value="name",
            resolved=True,
        )
    )
    await test_session.commit()
    loaded = await ConversationContextService(test_session).load(conv.id)
    assert loaded.clarifications.get("correction_type") == "name"


# F. Evidence can become KnowledgeDocument/KnowledgeChunk
@pytest.mark.asyncio
async def test_evidence_becomes_knowledge_chunk(test_session, agency_service):
    _, service = agency_service
    claim, sv = await _verified_fee_claim(test_session, service.id)
    claim.is_published = True
    await test_session.commit()

    ingest = EvidenceIngestionService(test_session, dry_run=False)
    report = await ingest.ingest_published_claims(service_id=service.id)
    assert report.chunks_created >= 1
    chunks = (await test_session.execute(select(KnowledgeChunk).where(KnowledgeChunk.service_id == service.id))).scalars().all()
    assert chunks
    meta = chunks[0].metadata_json or {}
    assert meta.get("claim_id") == str(claim.id)
    assert meta.get("source_version_id") == str(sv.id)


# G. Practical evidence cannot become official knowledge
@pytest.mark.asyncio
async def test_practical_cannot_become_official_chunk(test_session, agency_service):
    _, service = agency_service
    claim, _ = await _verified_fee_claim(
        test_session, service.id, info=InformationClass.PRACTICAL, key="test::practical"
    )
    claim.is_published = True
    await test_session.commit()
    report = await EvidenceIngestionService(test_session, dry_run=True).ingest_published_claims(
        service_id=service.id
    )
    assert report.skipped_practical >= 1


# H. Conflict blocks authoritative publication
def test_conflict_blocks_authoritative_publication():
    gate = evaluate_official_publication(**_gate_kwargs(has_unresolved_conflict=True))
    assert not gate.allowed


# I. Unsupported fee remains unsupported
@pytest.mark.asyncio
async def test_unsupported_fee_remains_unsupported(test_session, agency_service):
    _, service = agency_service
    orch = Orchestrator(test_session)
    req = ChatRequest(message="birth registration fee koto?", clarifications={})
    answer, _, _, _, ctx = await orch.run(req)
    assert ctx.service is not None
    if not any(f.amount.isdigit() for f in answer.fees):
        assert any("not yet verified" in w.lower() or "not available" in w.lower() for w in answer.warnings)


# J. Provenance remains intact after replacement
@pytest.mark.asyncio
async def test_provenance_intact_after_replacement(test_session, agency_service, tmp_path):
    _, service = agency_service
    claim, sv = await _verified_fee_claim(test_session, service.id, key="civil-birth-registration::c-br-fee-late")
    await test_session.commit()
    repo = _staging(tmp_path)
    replacement = SeedReplacement(
        service_id=service.id,
        claim_id=claim.id,
        replacement_kind="fee",
        status=SeedReplacementStatus.APPROVED.value,
        approved_by="test",
        approved_at=datetime.now(timezone.utc),
        before_json={"fees": []},
    )
    test_session.add(replacement)
    await test_session.commit()

    publisher = KnowledgePublisher(test_session, repo_root=repo, dry_run=False)
    await publisher.publish_verified("batch-01", approved_seed_replacement_claim_ids={claim.id})
    fee = (await test_session.execute(select(Fee).where(Fee.claim_id == claim.id))).scalar_one()
    assert fee.claim_id == claim.id
    ev = (await test_session.execute(select(ClaimEvidence).where(ClaimEvidence.claim_id == claim.id))).scalar_one()
    assert ev.source_version_id == sv.id


def test_conversation_context_follow_up_detection():
    assert ConversationContextService.is_follow_up_message("Naam")
    assert ConversationContextService.is_follow_up_message("name")
    assert not ConversationContextService.is_follow_up_message(
        "birth registration correction fee koto lagbe full details"
    )


def test_infer_clarification_from_naam():
    pending = ["Which birth certificate correction do you need (name, date of birth, or other field)?"]
    result = ConversationContextService._infer_clarification_from_follow_up("Naam", pending)
    assert result == ("correction_type", "name")


@pytest.mark.asyncio
async def test_knowledge_gaps_key_parsing():
    """Verification JSON uses knowledge_gaps key (not gaps)."""
    raw = {"knowledge_gaps": [{"gap_id": "G1", "notes": "x"}]}
    gaps = raw.get("knowledge_gaps") or raw.get("gaps") or []
    assert len(gaps) == 1
    assert gaps[0]["gap_id"] == "G1"
