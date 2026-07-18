# CONTRIBUTING_GUIDE.md

# Developer Onboarding Guide

Welcome to the AI-ATS engineering team! 

## Getting Started

1. **Install Prerequisites**:
   - Python 3.11+
   - Node.js v20+
   - Docker Desktop
   - Make

2. **Clone and Setup**:
   ```bash
   git clone https://github.com/your-org/ai-ats.git
   cd ai-ats
   cp .env.example .env
   make setup
   ```

3. **Database Setup**:
   Ensure Docker is running, then execute:
   ```bash
   make docker-up
   make migrate
   ```

4. **Running the Application**:
   ```bash
   make dev
   ```

## Repository Structure Overview

- `backend/`: FastAPI Python code.
  - `models/`: SQLAlchemy ORM models.
  - `schemas/`: Pydantic validation models.
  - `api/routers/`: HTTP endpoints.
  - `services/`: Business logic.
  - `repositories/`: Database queries.
  - `core/`: Config, DB connections, Security logic.
- `frontend/`: Next.js TypeScript code.
  - `app/`: Pages and routing.
  - `components/`: UI components.
  - `lib/`: Utilities, API clients.
- `docs/`: Technical specifications.

## Your First Pull Request
1. Pick an issue tagged `good-first-issue`.
2. Create a branch: `git checkout -b feat/my-new-feature`.
3. Write your code, following the `CODING_STANDARDS.md`.
4. Ensure tests pass (`make test`).
5. Open a Pull Request on GitHub.
