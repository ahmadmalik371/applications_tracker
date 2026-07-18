# TESTING_STRATEGY.md

# AI-ATS Testing Strategy

We follow the standard Testing Pyramid.

## 1. Unit Tests (Backend: `pytest`, Frontend: `vitest`)
- **Scope**: Individual functions, services, and utilities.
- **Rules**: 
  - Must not hit the real database. Use mocks or a fast in-memory SQLite equivalent.
  - Coverage goal: > 80%.
  - Execution time: < 10 seconds total.

## 2. Integration Tests
- **Scope**: Database repositories, Celery tasks, and API endpoints.
- **Rules**:
  - Spin up a real PostgreSQL container (via `pytest-docker` or Testcontainers).
  - Seed the database with fixtures.
  - Test the full request lifecycle (Router -> Service -> Repo -> DB).
  - Explicitly test multi-tenant boundaries (ensure User A cannot read User B's org data).

## 3. End-to-End (E2E) Tests (`Playwright`)
- **Scope**: Critical user journeys (Login, Post a Job, Upload Resume, Rank Candidate).
- **Rules**:
  - Runs against a fully deployed staging environment.
  - Runs on a nightly schedule and prior to production releases.

## 4. AI Specific Testing
- **Resume Parsing Eval**: Run the parsing pipeline against a golden dataset of 100 varied resumes. Check precision/recall of extracted skills.
- **Ranking Sanity Checks**: Ensure exact-match candidates receive scores > 95. Ensure zero-match candidates receive scores < 20.
