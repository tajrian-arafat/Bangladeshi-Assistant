"""Service routing unit tests."""

from __future__ import annotations

import pytest

from app.ai.routing.domain_entities import extract_domain_entities
from app.ai.routing.intent_classifier import classify_intent, classify_intents
from app.ai.routing.loader import capability_profiles_by_slug, load_phrase_hints


def test_classify_fee_inquiry_epassport() -> None:
    result = classify_intents("e-passport fee koto?")
    assert result.primary == "fee_inquiry"


def test_classify_status_intent() -> None:
    result = classify_intents("passport status check korbo kivabe?")
    assert result.primary == "status"


def test_classify_appointment_intent() -> None:
    result = classify_intents("passport appointment kothay?")
    assert result.primary == "appointment"


def test_classify_multi_intent_fee_and_documents() -> None:
    result = classify_intents("e-passport renew korte koto taka lage ebong ki ki lage?")
    assert result.primary in {"fee_inquiry", "document_list", "renewal"}
    assert len(result.all_intents) >= 2


def test_legacy_classify_intent_documents() -> None:
    result = classify_intent("passport renew documents lagbe")
    assert result in {"document_list", "procedure_inquiry"}


def test_legacy_classify_intent_fee() -> None:
    assert classify_intent("NID correction fee koto?") == "fee_inquiry"


def test_domain_entities_epassport_fee() -> None:
    entities = extract_domain_entities("e passport 48 page express fee koto")
    assert entities.passport_type == "e_passport"
    assert "passport" in entities.domains
    assert entities.action in {"fee", None} or entities.speed == "express"


def test_domain_entities_mrp_reissue() -> None:
    entities = extract_domain_entities("MRP reissue korte chai")
    assert entities.passport_type == "mrp"
    assert entities.action in {"reissue", "renewal"}


def test_phrase_hints_include_passport_fee() -> None:
    hints = dict(load_phrase_hints())
    assert hints.get("e-passport fee") == "epassport-fee-payment"
    assert hints.get("passport status check") == "epassport-application-status"


def test_capability_profiles_cover_passport_fee() -> None:
    profiles = capability_profiles_by_slug()
    fee = profiles["epassport-fee-payment"]
    assert "fee_inquiry" in fee["intent_capabilities"]
    assert fee["service_type"] == "fee_payment"


@pytest.mark.asyncio
async def test_service_router_fee_query(test_session) -> None:
    from app.ai.routing.intent_classifier import classify_intents
    from app.ai.routing.service_router import ServiceRouter
    from app.domain.models.knowledge import Agency, Service

    agency = Agency(slug="dip", name_en="DIP", name_bn="DIP")
    test_session.add(agency)
    await test_session.flush()

    for slug, name in [
        ("epassport-fee-payment", "E-Passport Fee Payment"),
        ("passport-mrp-initial", "MRP Initial Passport"),
    ]:
        test_session.add(
            Service(
                slug=slug,
                name_en=name,
                name_bn=name,
                category="PASSPORT_IMMIGRATION",
                status="ACTIVE",
                agency_id=agency.id,
            )
        )
    await test_session.commit()

    intents = classify_intents("e-passport fee koto?")
    router = ServiceRouter(test_session)
    result = await router.route("e-passport fee koto?", intents=intents)
    assert result.service is not None
    assert result.service.slug == "epassport-fee-payment"


@pytest.mark.asyncio
async def test_service_router_status_query(test_session) -> None:
    from app.ai.routing.intent_classifier import classify_intents
    from app.ai.routing.service_router import ServiceRouter
    from app.domain.models.knowledge import Agency, Service

    agency = Agency(slug="dip2", name_en="DIP", name_bn="DIP")
    test_session.add(agency)
    await test_session.flush()

    for slug, name in [
        ("epassport-application-status", "E-Passport Application Status"),
        ("epassport-new-application", "E-Passport New Application"),
    ]:
        test_session.add(
            Service(
                slug=slug,
                name_en=name,
                name_bn=name,
                category="PASSPORT_IMMIGRATION",
                status="ACTIVE",
                agency_id=agency.id,
            )
        )
    await test_session.commit()

    intents = classify_intents("passport status check korbo kivabe?")
    router = ServiceRouter(test_session)
    result = await router.route("passport status check korbo kivabe?", intents=intents)
    assert result.service is not None
    assert result.service.slug == "epassport-application-status"


@pytest.mark.asyncio
async def test_service_router_birth_registration(test_session) -> None:
    from app.ai.routing.intent_classifier import classify_intents
    from app.ai.routing.service_router import ServiceRouter
    from app.domain.models.knowledge import Agency, Service

    agency = Agency(slug="bdris", name_en="BDRIS", name_bn="BDRIS")
    test_session.add(agency)
    await test_session.flush()

    test_session.add(
        Service(
            slug="birth-registration",
            name_en="Birth Registration",
            name_bn="জন্ম নিবন্ধন",
            category="CIVIL_REGISTRATION",
            status="ACTIVE",
            agency_id=agency.id,
        )
    )
    await test_session.commit()

    intents = classify_intents("জন্ম নিবন্ধন করতে কী লাগে?")
    router = ServiceRouter(test_session)
    result = await router.route("জন্ম নিবন্ধন করতে কী লাগে?", intents=intents)
    assert result.service is not None
    assert result.service.slug == "birth-registration"
