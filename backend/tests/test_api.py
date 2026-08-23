"""API integration tests."""

import pytest
from httpx import AsyncClient

from app.domain.models.geography import District, Division
from app.domain.models.knowledge import Agency, ChecklistItem, Service


@pytest.mark.asyncio
async def test_services_list_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/services")
    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.asyncio
async def test_chat_no_match(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/chat",
        json={"message": "random unknown query xyz", "language_preference": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["confidence"] == "low"
    assert "answer" in body


@pytest.mark.asyncio
async def test_chat_passport_match(client: AsyncClient, test_session) -> None:
    agency = Agency(slug="dip", name_bn="DIP", name_en="Department of Immigration and Passports")
    test_session.add(agency)
    await test_session.flush()
    service = Service(
        slug="passport-renewal",
        name_bn="পাসপোর্ট নবায়ন",
        name_en="Passport Renewal",
        aliases=["passport renew"],
        agency_id=agency.id,
        category="IDENTITY",
        status="ACTIVE",
    )
    test_session.add(service)
    await test_session.flush()
    test_session.add(
        ChecklistItem(
            service_id=service.id,
            order=1,
            item_type="REQUIRED",
            label_bn="NID",
            label_en="National Identity Card (NID)",
        )
    )
    await test_session.commit()

    response = await client.post(
        "/api/v1/chat",
        json={
            "message": "passport renew korte ki ki lagbe?",
            "language_preference": "auto",
            "clarifications": {
                "passport_type": "e-passport",
                "application_type": "renewal",
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["service_slug"] == "passport-renewal"
    assert len(body["answer"]["checklist"]) >= 1


@pytest.mark.asyncio
async def test_districts(client: AsyncClient, test_session) -> None:
    division = Division(slug="dhaka", name_bn="ঢাকা", name_en="Dhaka")
    test_session.add(division)
    await test_session.flush()
    test_session.add(District(division_id=division.id, slug="dhaka-district", name_bn="ঢাকা", name_en="Dhaka"))
    await test_session.commit()

    response = await client.get("/api/v1/districts")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
