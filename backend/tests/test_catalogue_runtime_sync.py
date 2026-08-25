"""Catalogue → runtime Service sync tests."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.knowledge.catalogue_runtime_sync import CatalogueRuntimeSync
from app.core.exceptions import ValidationError
from app.domain.enums import CatalogueMappingStatus
from app.domain.models.claims import ServiceCatalogueMapping
from app.domain.models.knowledge import Agency, Service


def _write_mini_repo(tmp_path: Path) -> Path:
    cat_dir = tmp_path / "data" / "service_catalogue"
    research = tmp_path / "data" / "research"
    cat_dir.mkdir(parents=True)
    research.mkdir(parents=True)

    services = {
        "catalogue_version": "1.0.0-finalized",
        "services": [
            {
                "service_id": "civil-birth-registration",
                "service_name_bn": "জন্ম নিবন্ধন",
                "service_name_en": "Birth Registration",
                "aliases": ["birth reg"],
                "category": "CIVIL_REGISTRATION",
                "authority_id": "orgbdr",
                "status": "CONFIRMED",
                "catalogue_version": "1.0.0-finalized",
                "official_source": "https://bdris.gov.bd/",
            },
            {
                "service_id": "nid-card-info-correction",
                "service_name_bn": "এনআইডি সংশোধন",
                "service_name_en": "NID Card Info Correction",
                "aliases": [],
                "category": "IDENTITY",
                "authority_id": "ec-nid",
                "status": "CONFIRMED",
                "catalogue_version": "1.0.0-finalized",
            },
            {
                "service_id": "nid-other-info-correction",
                "service_name_bn": "এনআইডি অন্যান্য সংশোধন",
                "service_name_en": "NID Other Info Correction",
                "aliases": [],
                "category": "IDENTITY",
                "authority_id": "ec-nid",
                "status": "CONFIRMED",
                "catalogue_version": "1.0.0-finalized",
            },
            {
                "service_id": "nid-new-voter-registration",
                "service_name_bn": "নতুন ভোটার",
                "service_name_en": "New Voter Registration",
                "aliases": [],
                "category": "IDENTITY",
                "authority_id": "ec-nid",
                "status": "CONFIRMED",
                "catalogue_version": "1.0.0-finalized",
            },
            {
                "service_id": "agri-seed-certification",
                "service_name_bn": "বীজ",
                "service_name_en": "Seed Certification",
                "aliases": [],
                "category": "AGRICULTURE",
                "authority_id": "dae",
                "status": "UNVERIFIED",
                "catalogue_version": "1.0.0-finalized",
            },
        ],
    }
    redirects = {
        "redirects": [
            {
                "service_id": "old-dup",
                "status": "DUPLICATE",
                "canonical_service_id": "nid-new-voter-registration",
            },
            {"service_id": "not-real", "status": "NOT_A_SERVICE"},
        ]
    }
    authorities = {
        "authorities": [
            {"authority_id": "ec-nid", "name_en": "Election Commission NID", "name_bn": "ইসি"},
            {"authority_id": "orgbdr", "name_en": "ORGBDR", "name_bn": "জেনারেল"},
            {"authority_id": "dae", "name_en": "DAE", "name_bn": "কৃষি"},
        ]
    }
    mappings = {
        "mvp_seed_slugs": ["birth-registration", "nid-correction"],
        "mappings": [
            {
                "catalogue_service_id": "civil-birth-registration",
                "runtime_slug": "birth-registration",
                "mapping_type": "existing_seed",
                "review_status": "NEEDS_REVIEW",
                "allow_overwrite_seed": False,
            },
            {
                "catalogue_service_id": "nid-card-info-correction",
                "runtime_slug": "nid-correction",
                "mapping_type": "existing_seed",
                "review_status": "NEEDS_REVIEW",
                "allow_overwrite_seed": False,
            },
            {
                "catalogue_service_id": "nid-other-info-correction",
                "runtime_slug": "nid-correction",
                "mapping_type": "alias",
                "review_status": "NEEDS_REVIEW",
                "allow_overwrite_seed": False,
            },
        ],
    }
    (cat_dir / "services.json").write_text(json.dumps(services), encoding="utf-8")
    (cat_dir / "redirects.json").write_text(json.dumps(redirects), encoding="utf-8")
    (cat_dir / "authorities.json").write_text(json.dumps(authorities), encoding="utf-8")
    (research / "catalogue_runtime_mappings.json").write_text(
        json.dumps(mappings), encoding="utf-8"
    )
    return tmp_path


@pytest_asyncio.fixture
async def seeded(test_session: AsyncSession):
    agency = Agency(slug="ec-nid", name_bn="ইসি", name_en="EC NID")
    test_session.add(agency)
    await test_session.flush()
    birth = Service(
        slug="birth-registration",
        name_bn="জন্ম",
        name_en="Birth Registration",
        agency_id=agency.id,
        category="CIVIL_REGISTRATION",
        status="UNDER_REVIEW",
        review_state="DRAFT",
    )
    nid = Service(
        slug="nid-correction",
        name_bn="এনআইডি",
        name_en="NID Correction",
        agency_id=agency.id,
        category="IDENTITY",
        status="UNDER_REVIEW",
        review_state="DRAFT",
    )
    test_session.add_all([birth, nid])
    await test_session.commit()
    return agency, birth, nid


@pytest.mark.asyncio
async def test_existing_mvp_service_mapping(test_session: AsyncSession, seeded, tmp_path):
    _write_mini_repo(tmp_path)
    syncer = CatalogueRuntimeSync(test_session, repo_root=tmp_path, dry_run=False)
    report = await syncer.sync()
    await test_session.commit()
    assert report.ok
    maps = (
        await test_session.execute(select(ServiceCatalogueMapping))
    ).scalars().all()
    by_c = {m.catalogue_service_id: m for m in maps}
    assert by_c["civil-birth-registration"].runtime_slug == "birth-registration"
    assert by_c["civil-birth-registration"].mapping_status == CatalogueMappingStatus.EXACT_MATCH.value
    assert by_c["nid-card-info-correction"].runtime_slug == "nid-correction"


@pytest.mark.asyncio
async def test_new_canonical_service_creation(test_session: AsyncSession, seeded, tmp_path):
    _write_mini_repo(tmp_path)
    syncer = CatalogueRuntimeSync(test_session, repo_root=tmp_path, dry_run=False)
    await syncer.sync()
    await test_session.commit()
    svc = (
        await test_session.execute(
            select(Service).where(Service.slug == "nid-new-voter-registration")
        )
    ).scalar_one()
    assert svc.catalogue_service_id == "nid-new-voter-registration"
    assert svc.status == "UNDER_REVIEW"


@pytest.mark.asyncio
async def test_duplicate_prevention(test_session: AsyncSession, seeded, tmp_path):
    _write_mini_repo(tmp_path)
    syncer = CatalogueRuntimeSync(test_session, repo_root=tmp_path, dry_run=False)
    await syncer.sync()
    await test_session.commit()
    count1 = (
        await test_session.execute(select(Service))
    ).scalars().all()
    n1 = len(count1)
    # second run
    report2 = await CatalogueRuntimeSync(test_session, repo_root=tmp_path, dry_run=False).sync()
    await test_session.commit()
    count2 = (
        await test_session.execute(select(Service))
    ).scalars().all()
    assert len(count2) == n1
    assert report2.proposed_create_services == 0


@pytest.mark.asyncio
async def test_unverified_service_exclusion(test_session: AsyncSession, seeded, tmp_path):
    _write_mini_repo(tmp_path)
    await CatalogueRuntimeSync(test_session, repo_root=tmp_path, dry_run=False).sync()
    await test_session.commit()
    bad = (
        await test_session.execute(
            select(Service).where(Service.slug == "agri-seed-certification")
        )
    ).scalar_one_or_none()
    assert bad is None
    mapped = (
        await test_session.execute(
            select(ServiceCatalogueMapping).where(
                ServiceCatalogueMapping.catalogue_service_id == "agri-seed-certification"
            )
        )
    ).scalar_one_or_none()
    assert mapped is None


@pytest.mark.asyncio
async def test_alias_mapping(test_session: AsyncSession, seeded, tmp_path):
    _write_mini_repo(tmp_path)
    await CatalogueRuntimeSync(test_session, repo_root=tmp_path, dry_run=False).sync()
    await test_session.commit()
    m = (
        await test_session.execute(
            select(ServiceCatalogueMapping).where(
                ServiceCatalogueMapping.catalogue_service_id == "nid-other-info-correction"
            )
        )
    ).scalar_one()
    assert m.mapping_status == CatalogueMappingStatus.ALIAS_MATCH.value
    assert m.runtime_slug == "nid-correction"


@pytest.mark.asyncio
async def test_merge_mapping(test_session: AsyncSession, seeded, tmp_path):
    root = _write_mini_repo(tmp_path)
    # add merge mapping entry + confirmed service
    cat = json.loads((root / "data/service_catalogue/services.json").read_text())
    cat["services"].append(
        {
            "service_id": "birth-reg-legacy",
            "service_name_bn": "লিগ্যাসি",
            "service_name_en": "Legacy Birth",
            "aliases": [],
            "category": "CIVIL_REGISTRATION",
            "authority_id": "orgbdr",
            "status": "CONFIRMED",
            "catalogue_version": "1.0.0-finalized",
        }
    )
    (root / "data/service_catalogue/services.json").write_text(json.dumps(cat), encoding="utf-8")
    maps = json.loads((root / "data/research/catalogue_runtime_mappings.json").read_text())
    maps["mappings"].append(
        {
            "catalogue_service_id": "birth-reg-legacy",
            "runtime_slug": "birth-registration",
            "mapping_type": "merge",
            "review_status": "APPROVED",
            "allow_overwrite_seed": False,
        }
    )
    (root / "data/research/catalogue_runtime_mappings.json").write_text(
        json.dumps(maps), encoding="utf-8"
    )
    await CatalogueRuntimeSync(test_session, repo_root=tmp_path, dry_run=False).sync()
    await test_session.commit()
    m = (
        await test_session.execute(
            select(ServiceCatalogueMapping).where(
                ServiceCatalogueMapping.catalogue_service_id == "birth-reg-legacy"
            )
        )
    ).scalar_one()
    assert m.mapping_status == CatalogueMappingStatus.MERGED_MATCH.value


@pytest.mark.asyncio
async def test_rerun_without_duplicates(test_session: AsyncSession, seeded, tmp_path):
    _write_mini_repo(tmp_path)
    s = CatalogueRuntimeSync(test_session, repo_root=tmp_path, dry_run=False)
    r1 = await s.sync()
    await test_session.commit()
    r2 = await CatalogueRuntimeSync(test_session, repo_root=tmp_path, dry_run=False).sync()
    await test_session.commit()
    assert r1.ok and r2.ok
    assert r2.proposed_create_services == 0
    services = (await test_session.execute(select(Service))).scalars().all()
    slugs = [s.slug for s in services]
    assert len(slugs) == len(set(slugs))


@pytest.mark.asyncio
async def test_rollback_on_failure(test_session: AsyncSession, seeded, tmp_path):
    root = _write_mini_repo(tmp_path)
    before = len((await test_session.execute(select(Service))).scalars().all())

    syncer = CatalogueRuntimeSync(test_session, repo_root=root, dry_run=False)
    original = syncer._upsert_mapping

    async def boom(*args, **kwargs):
        changed = await original(*args, **kwargs)
        # After first successful write path creates mappings/services, force failure
        raise ValidationError("forced failure for rollback test")

    syncer._upsert_mapping = boom  # type: ignore[method-assign]
    with pytest.raises(ValidationError, match="forced failure"):
        await syncer.sync()

    # session_scope isn't used here — publisher rolls back on ValidationError inside sync()
    # Re-query: either rolled back to before, or session invalidated; refresh
    await test_session.rollback()
    after = (await test_session.execute(select(Service))).scalars().all()
    # Pre-existing MVP seeds remain; no new canonical row persisted from failed txn
    assert len(after) == before
    assert all(s.slug in {"birth-registration", "nid-correction"} for s in after)
