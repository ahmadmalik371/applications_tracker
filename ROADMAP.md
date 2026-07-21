# ROADMAP.md

# AI-ATS Development Roadmap

## Phase 1: Foundation (Current)
*Focus: Project scaffolding, infrastructure, and core authentication.*

- [x] Repository scaffolding & documentation
- [ ] Database schema setup (Alembic + SQLAlchemy models)
- [ ] Docker infrastructure (Postgres, Redis)
- [ ] Base FastAPI setup with centralized error handling
- [ ] JWT Authentication & User Registration
- [ ] Organization creation and multi-tenant scoping
- [ ] Role-Based Access Control (RBAC) middleware

## Phase 2: Core ATS
*Focus: Jobs, Candidates, and Applications (The CRUD).*

- [ ] Job Management (Create, List, Update, Status)
- [ ] Candidate Profiles (Manual entry)
- [ ] Job Application pipeline (Applied -> Hired)
- [ ] Application status transitions
- [ ] Basic Next.js Frontend scaffolding
- [ ] UI for Job Board and Candidate Pipeline

## Phase 3: AI Pipeline Integration
*Focus: The "AI" in AI-ATS.*

- [ ] Celery worker setup
- [ ] S3 integration for Resume uploads
- [ ] Resume Parsing task (PDF extraction + LLM structuring)
- [ ] Job and Candidate Embedding generation
- [ ] pgvector similarity search implementation
- [ ] Tabular ML Ranker training/integration
- [ ] Explainability generation (SHAP summary)

## Phase 4: Advanced Features
*Focus: Interviews, Offers, and Analytics.*

- [ ] Interview scheduling module
- [ ] Interviewer scorecards
- [ ] Offer generation and approval workflow
- [ ] Analytics dashboard (Time-to-hire, Conversion rates)
- [ ] Email notifications
- [ ] Audit Logging implementation

## Phase 5: Scale & Polish
*Focus: Production readiness.*

- [ ] Rate limiting implementation
- [ ] Comprehensive E2E tests
- [ ] Kubernetes manifest generation
- [ ] Prometheus/Grafana monitoring integration
- [ ] Performance optimization (Caching)
- [ ] Final security audit
