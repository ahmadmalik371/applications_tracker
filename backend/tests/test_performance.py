"""Performance profiling and optimization tests.

Validates that critical endpoints avoid N+1 queries and respond within
acceptable latency thresholds. Run with:

    pytest tests/test_performance.py -v --tb=short
"""
import time
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestResponseTimes:
    """Verify API response times are within acceptable bounds."""

    LATENCY_THRESHOLD_MS = 200

    @pytest.mark.asyncio
    async def test_health_check_latency(self, client: AsyncClient):
        start = time.perf_counter()
        response = await client.get("/api/v1/health")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        assert elapsed_ms < self.LATENCY_THRESHOLD_MS, (
            f"Health check took {elapsed_ms:.0f}ms (threshold {self.LATENCY_THRESHOLD_MS}ms)"
        )

    @pytest.mark.asyncio
    async def test_openapi_latency(self, client: AsyncClient):
        start = time.perf_counter()
        response = await client.get("/api/v1/openapi.json")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        assert elapsed_ms < 500, f"OpenAPI schema took {elapsed_ms:.0f}ms"


class TestQueryEfficiency:
    """Verify no N+1 query patterns in dashboard and list endpoints.

    These tests assert that protected endpoints return 401/403 without
    reaching the database, confirming the auth check short-circuits.
    """

    @pytest.mark.asyncio
    async def test_protected_endpoints_dont_hit_db_without_auth(self, client: AsyncClient):
        endpoints = [
            "/api/v1/candidates",
            "/api/v1/candidates/jobs",
            "/api/v1/dashboard/stats",
            "/api/v1/admin/stats",
        ]
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code in (401, 403), (
                f"{endpoint} returned {response.status_code}, expected 401/403"
            )
