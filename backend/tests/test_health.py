"""Health and readiness endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_readiness_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/v1/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["checks"]) >= 1
    db_check = next(c for c in data["checks"] if c["name"] == "database")
    assert db_check["status"] == "ok"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["health"] == "/api/v1/health"
