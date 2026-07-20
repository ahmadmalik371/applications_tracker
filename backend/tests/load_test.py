"""Locust load testing scenarios for AI-ATS.

Run with:
    cd backend && locust -f tests/load_test.py --host=http://localhost:8000

Scenarios:
    - High concurrency: API read endpoints under heavy load
    - Bulk uploads: Resume upload simulation
    - Heavy AI ranking: Ranking endpoints with large candidate sets
    - Complex search: Hybrid search with varied queries
"""
from locust import HttpUser, task, between, tag


class ATSUser(HttpUser):
    """Simulates a recruiter using the ATS."""

    wait_time = between(1, 5)

    def on_start(self):
        """Login to get auth token."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "loadtest@test.com",
            "password": "LoadTest123!",
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @tag("read")
    @task(3)
    def list_candidates(self):
        self.client.get("/api/v1/candidates?limit=50", headers=self.headers)

    @tag("read")
    @task(2)
    def list_jobs(self):
        self.client.get("/api/v1/candidates/jobs?limit=50", headers=self.headers)

    @tag("read")
    @task(2)
    def dashboard_stats(self):
        self.client.get("/api/v1/dashboard/stats", headers=self.headers)

    @tag("ai")
    @task(2)
    def rank_candidates(self):
        self.client.get(
            "/api/v1/rankings/candidates/for-job/00000000-0000-0000-0000-000000000000",
            headers=self.headers,
        )

    @tag("search")
    @task(2)
    def hybrid_search(self):
        self.client.get(
            "/api/v1/candidates/search/hybrid",
            params={"q": "python developer fastapi", "limit": 20},
            headers=self.headers,
        )

    @tag("ai")
    @task(1)
    def ai_search(self):
        self.client.get(
            "/api/v1/ai-assistant/search",
            params={"q": "senior backend engineer", "limit": 10},
            headers=self.headers,
        )

    @tag("upload")
    @task(1)
    def upload_resume(self):
        import io
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
        files = {"file": ("resume.pdf", fake_pdf, "application/pdf")}
        self.client.post(
            "/api/v1/candidates/00000000-0000-0000-0000-000000000000/upload-resume",
            files=files,
            headers=self.headers,
        )


class HighConcurrencyUser(HttpUser):
    """Aggressive user for stress testing."""

    wait_time = between(0.1, 0.5)

    @task
    def rapid_health_checks(self):
        self.client.get("/health")
