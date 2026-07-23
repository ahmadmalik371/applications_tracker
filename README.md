# AI-ATS

AI-ATS is a production-grade, enterprise-ready, multi-tenant Applicant Tracking System (ATS) powered by Machine Learning and semantic vector search.

It is designed to handle millions of candidates and jobs across thousands of organizations securely and efficiently.

## Core Features

- **Multi-Tenant Architecture**: Strict data isolation for SaaS deployment.
- **AI-Powered Resume Parsing**: Extract structured data from unstructured PDFs/DOCXs using LLMs.
- **Semantic Candidate Matching**: `pgvector`-backed embedding search to match candidates to job requirements.
- **Explainable AI**: Understand *why* a candidate was ranked highly with transparent ML models.
- **Full Recruiting Lifecycle**: Manage jobs, candidates, applications, interviews, and offers.
- **Role-Based Access Control**: Secure, granular permissions for Recruiters, Hiring Managers, and Admins.

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic, Celery
- **Frontend**: Next.js 16, TypeScript, TailwindCSS
- **Database**: PostgreSQL 16 with the `pgvector` extension
- **Cache/Broker**: Redis
- **Infrastructure**: Docker, Docker Compose

## Verified Local Development Setup

This repository is now wired for a local browser-first dev workflow with the frontend proxying API traffic to the backend on `http://localhost:8000/api/v1`.

### Prerequisites

- Docker and Docker Compose
- Node.js (v20+)
- Python (v3.11+)

### Start the local stack

1. Start the database, Redis, and backend containers:

   ```bash
   docker compose up -d db redis backend
   ```

2. Start the frontend in a separate terminal:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open the app at:

   ```text
   http://localhost:3000
   ```

### Verified runtime ports

- PostgreSQL: `5433` on the host
- Redis: `6380` on the host
- Backend API: `8000`
- Frontend UI: `3000`

### Demo login

Use the seeded admin account for local verification:

- Email: `admin@techcorp.com`
- Password: `password123`

### Health and verification

A live health check is available through the frontend proxy:

```bash
curl http://localhost:3000/api/v1/health
```

Expected response:

```json
{"success":true,"status":"ok","version":"1.0.0","environment":"development","database":"ok"}
```

### Environment notes

- The backend service uses the Docker internal network hostnames for the containers.
- The browser-side frontend is configured to use `NEXT_PUBLIC_API_URL` or the localhost API fallback.
- Local host ports were moved off the default `5432` / `6379` conflict-prone values to `5433` / `6380` so the app can run cleanly on developer machines.

## Documentation Directory

Comprehensive documentation is available in the repository:

- [System Architecture](ARCHITECTURE.md)
- [Database Schema](DATABASE.md)
- [API Specification](API_SPEC.md)
- [ML Pipeline](ML_PIPELINE.md)
- [Project Requirements](PROJECT_REQUIREMENTS.md)
- [Security Policy](SECURITY.md)
- [Deployment Guide](DEPLOYMENT.md)

Detailed module specifications are found in the `docs/` folder.

## License

MIT License. See [LICENSE](LICENSE) for details.
