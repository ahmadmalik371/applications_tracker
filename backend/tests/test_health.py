import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_200(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_response_body(client: AsyncClient):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert data["database"] == "ok"
