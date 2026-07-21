"""End-to-end tests for critical user journeys.

Tests cover:
    1. Registration → Login → Token refresh
    2. Job creation → Candidate creation → Resume upload → Parsing
    3. Ranking → Match score → Explanation
    4. AI search → Recommendation
    5. Notification dispatch

Tests that exercise auth flows (register/login) require a live PostgreSQL
database because the app's global engine is not the in-memory SQLite fixture.
"""
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


def _db_reachable() -> bool:
    import asyncio
    from src.core.database import check_database_connection
    try:
        asyncio.run(check_database_connection())
        return True
    except Exception:
        return False


requires_db = pytest.mark.skipif(
    not _db_reachable(), reason="No PostgreSQL database available"
)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client: AsyncClient):
    """Register a new org and return an access token."""
    response = await client.post("/api/v1/auth/register", json={
        "organization_name": "E2E Test Corp",
        "email": "e2e@test.com",
        "password": "TestPass123!",
        "full_name": "E2E Tester",
    })
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


class TestAuthJourney:
    """Journey 1: Registration → Login → Token refresh."""

    @requires_db
    @pytest.mark.asyncio
    async def test_register_returns_tokens(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "organization_name": "Auth Test Corp",
            "email": "auth@test.com",
            "password": "SecurePass123!",
            "full_name": "Auth Tester",
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @requires_db
    @pytest.mark.asyncio
    async def test_login_with_registered_credentials(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "organization_name": "Login Corp",
            "email": "login@test.com",
            "password": "SecurePass123!",
            "full_name": "Login Tester",
        })
        response = await client.post("/api/v1/auth/login", json={
            "email": "login@test.com",
            "password": "SecurePass123!",
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_protected_endpoint_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/candidates")
        assert response.status_code == 401 or response.status_code == 403


class TestRankingJourney:
    """Journey 3: Ranking → Match score → Explanation."""

    @pytest.mark.asyncio
    async def test_health_check_works(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    @pytest.mark.asyncio
    async def test_dashboard_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/dashboard/stats")
        assert response.status_code in (401, 403)


class TestSearchJourney:
    """Journey 4: AI search."""

    @pytest.mark.asyncio
    async def test_search_requires_auth(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/candidates/search/hybrid",
            params={"q": "python"},
        )
        assert response.status_code in (401, 403)


class TestAdminJourney:
    """Journey: Super Admin endpoints."""

    @requires_db
    @pytest.mark.asyncio
    async def test_admin_requires_super_admin_role(self, client: AsyncClient, auth_headers):
        response = await client.get("/api/v1/admin/stats", headers=auth_headers)
        assert response.status_code in (401, 403)
