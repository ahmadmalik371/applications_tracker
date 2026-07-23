# TASKS.md

# AI-ATS Detailed Implementation Roadmap

This document outlines the complete implementation roadmap for AI-ATS, broken down into sequential milestones. Each milestone consists of independent tasks detailing the required work across all technical domains.

---

## Milestone 1: Platform Foundation & Infrastructure
**Objective**: Establish the core infrastructure, CI/CD, and the foundational multi-tenant data models.

### Task 1.1: Backend Project Initialization
- **Objective**: Scaffold the FastAPI backend with essential core configurations.
- **Dependencies**: None
- **Estimated Complexity**: Low
- **Backend Work**: Setup FastAPI app, CORS middleware, centralized exception handlers, structured JSON logging, and dependency injection framework.
- **Frontend Work**: None
- **Database Work**: Configure SQLAlchemy engine, async session maker, and connection pooling. Initialize Alembic.
- **AI Work**: None
- **Testing Requirements**: Unit tests for exception handlers and config loading.

### Task 1.2: Multi-Tenant Data Models
- **Objective**: Create the core database tables that govern tenant isolation.
- **Dependencies**: Task 1.1
- **Estimated Complexity**: Medium
- **Backend Work**: Define SQLAlchemy models for `Organization` and `User`. Implement `get_current_tenant` dependency.
- **Frontend Work**: None
- **Database Work**: Alembic migration for `organizations` and `users` tables. Enforce unique constraints (e.g., `email` per `organization_id`).
- **AI Work**: None
- **Testing Requirements**: Integration tests verifying cross-tenant data access is blocked.

### Task 1.3: Authentication & RBAC
- **Objective**: Implement secure user registration, login, and Role-Based Access Control.
- **Dependencies**: Task 1.2
- **Estimated Complexity**: High
- **Backend Work**: Implement password hashing (Argon2), JWT generation/validation, login/register endpoints, and `require_role` middleware.
- **Frontend Work**: Setup Next.js App Router, implement Auth Context, Login page, and Registration page.
- **Database Work**: None (using models from 1.2).
- **AI Work**: None
- **Testing Requirements**: API tests for login failure states, token expiry, and RBAC rejection (403 Forbidden).

---

## Milestone 2: Core ATS (CRUD & Pipeline)
**Objective**: Build the standard ATS functionality allowing recruiters to post jobs and move candidates through a hiring pipeline.

### Task 2.1: Job Management
- **Objective**: Allow organizations to create, read, update, and archive job postings.
- **Dependencies**: Task 1.3
- **Estimated Complexity**: Medium
- **Backend Work**: Implement Job Services, Repositories, and API endpoints (CRUD).
- **Frontend Work**: Build Job Dashboard, Job Creation form (with React Hook Form + Zod), and Job Details page.
- **Database Work**: Alembic migrations for `jobs` and `job_skills` tables.
- **AI Work**: None
- **Testing Requirements**: E2E test for creating a job posting; unit tests for Job Service validation.

### Task 2.2: Application Pipeline Data Models
- **Objective**: Establish the relational structure for candidates and applications.
- **Dependencies**: Task 2.1
- **Estimated Complexity**: Medium
- **Backend Work**: Implement Candidate and Application Services, Repositories, and API endpoints.
- **Frontend Work**: None
- **Database Work**: Alembic migrations for `candidates` and `applications` tables. Add multi-tenant foreign keys.
- **AI Work**: None
- **Testing Requirements**: Integration tests for Application stage transitions and constraints.

### Task 2.3: Kanban Pipeline UI
- **Objective**: Build the visual Kanban board for managing applications.
- **Dependencies**: Task 2.2
- **Estimated Complexity**: High
- **Backend Work**: Create optimized endpoints to fetch applications grouped by stage.
- **Frontend Work**: Implement drag-and-drop Kanban board using Shadcn UI components. Implement optimistic UI updates using TanStack Query.
- **Database Work**: Add indexes on `applications.stage` and `applications.job_id`.
- **AI Work**: None
- **Testing Requirements**: Frontend component tests for drag-and-drop state changes.

---

## Milestone 3: AI Pipeline Integration
**Objective**: Introduce asynchronous processing, vector embeddings, and LLM-powered resume parsing.

### Task 3.1: Asynchronous Task Infrastructure
- **Objective**: Set up Celery and Redis to handle background jobs without blocking the API.
- **Dependencies**: Task 1.1
- **Estimated Complexity**: Medium
- **Backend Work**: Configure Celery worker, Redis broker, and define a base async task framework.
- **Frontend Work**: None
- **Database Work**: None
- **AI Work**: None
- **Testing Requirements**: Unit test for task enqueueing and worker execution.

### Task 3.2: Resume Upload & S3 Storage
- **Objective**: Enable secure resume uploads and object storage.
- **Dependencies**: Task 2.2, Task 3.1
- **Estimated Complexity**: Medium
- **Backend Work**: Implement S3 client (boto3). Create `/api/v1/candidates/{id}/resume` endpoint. Enqueue parse task.
- **Frontend Work**: Build file upload component (drag-and-drop, max 5MB validation, PDF/DOCX only).
- **Database Work**: Update `candidates` table to store `resume_url` (S3 path).
- **AI Work**: None
- **Testing Requirements**: API tests with mocked S3 client.

### Task 3.3: Resume Parsing Engine
- **Objective**: Extract structured data from uploaded PDFs using LLMs.
- **Dependencies**: Task 3.2
- **Estimated Complexity**: High
- **Backend Work**: Implement Celery task `parse_resume`. Write PyMuPDF text extraction logic.
- **Frontend Work**: Add UI indicators for "Processing" status on candidate profiles.
- **Database Work**: Update `candidates.parsed_data` (JSONB). Add GIN index for JSON queries.
- **AI Work**: Design and test the structured output extraction prompt using GPT-4o-mini or Claude 3.5 Haiku. Implement fallback parsing logic.
- **Testing Requirements**: Evaluation test suite running the prompt against 50 sample resumes; verify Pydantic schema validation.

### Task 3.4: Vector Embedding & pgvector Setup
- **Objective**: Generate and store dense vector embeddings for jobs and candidates.
- **Dependencies**: Task 2.1, Task 3.3
- **Estimated Complexity**: High
- **Backend Work**: Integrate embedding provider API (e.g., `text-embedding-3-small`).
- **Frontend Work**: None
- **Database Work**: Enable `pgvector` extension. Add `embedding` columns to `jobs` and `candidates`. Create HNSW indexes.
- **AI Work**: Implement batching strategy for embedding generation.
- **Testing Requirements**: Integration test verifying vector insertion and cosine similarity calculations in Postgres.

---

## Milestone 4: Candidate Ranking & Explainability
**Objective**: Calculate intelligent match scores using vector search and tabular ML, and present them with clear explanations.

### Task 4.1: Hybrid Vector Search
- **Objective**: Fetch the initial candidate pool using semantic similarity + business rules.
- **Dependencies**: Task 3.4
- **Estimated Complexity**: Medium
- **Backend Work**: Implement repository method executing `pgvector` similarity search combined with `organization_id` and strict rule pre-filtering.
- **Frontend Work**: None
- **Database Work**: Optimize HNSW index parameters (`m`, `ef_construction`).
- **AI Work**: None
- **Testing Requirements**: Performance testing to ensure query completes < 500ms for 100k rows.

### Task 4.2: Feature Engineering & ML Ranker
- **Objective**: Calculate the final 0-100 match score using XGBoost/LightGBM.
- **Dependencies**: Task 4.1
- **Estimated Complexity**: Very High
- **Backend Work**: Implement the `FeatureExtractor` (skills overlap, experience delta). Integrate the inference engine (e.g., load a pre-trained XGBoost model).
- **Frontend Work**: Display AI Match Scores on the Kanban board and candidate profiles.
- **Database Work**: Store latest `match_score` in the `applications` table.
- **AI Work**: Define the feature space. Train a global baseline Tabular ML model using synthetic or open-source hiring data.
- **Testing Requirements**: Offline metric evaluation (NDCG) using a hold-out test set.

### Task 4.3: AI Explainability Generation
- **Objective**: Generate human-readable reasons for a candidate's score.
- **Dependencies**: Task 4.2
- **Estimated Complexity**: High
- **Backend Work**: Calculate SHAP values post-inference. Pass SHAP outputs and raw features to an LLM to generate the explanation text.
- **Frontend Work**: Build the "AI Insights" panel showing Strengths, Weaknesses, and Confidence levels.
- **Database Work**: Cache explanations in Redis to reduce LLM costs on repeated views.
- **AI Work**: Prompt engineering for the explainability generation.
- **Testing Requirements**: Manual QA of the generated text to ensure professional tone and lack of hallucinations.

---

## Milestone 5: Scale, Polish & Advanced Workflows
**Objective**: Finalize the application for production deployment with monitoring, security, and advanced features.

### Task 5.1: Interview & Offer Workflows
- **Objective**: Allow scheduling interviews and generating offers.
- **Dependencies**: Task 2.2
- **Estimated Complexity**: Medium
- **Backend Work**: CRUD for `Interviews` and `Offers`. Implement state transitions (e.g., pending -> accepted).
- **Frontend Work**: Interview scheduling form, Scorecard submission UI, Offer details view.
- **Database Work**: Alembic migrations for `interviews`, `interviewers`, and `offers`.
- **AI Work**: None
- **Testing Requirements**: API tests for offer state machines (e.g., cannot accept a drafted offer).

### Task 5.2: Audit Logging & Security
- **Objective**: Meet enterprise security requirements for compliance.
- **Dependencies**: Task 1.1
- **Estimated Complexity**: Medium
- **Backend Work**: Implement an event listener or middleware that writes POST/PUT/DELETE actions to an audit log. Implement rate limiting (Redis sliding window).
- **Frontend Work**: None
- **Database Work**: Create `audit_logs` table with partitioning (by month).
- **AI Work**: Ensure PII scrubbing is active before any data touches external LLMs.
- **Testing Requirements**: Security audit; verify rate limits trigger 429 errors.

### Task 5.3: Observability & Deployment
- **Objective**: Ensure the system can be monitored and deployed reliably.
- **Dependencies**: Task 3.1
- **Estimated Complexity**: Medium
- **Backend Work**: Integrate Sentry for exception tracking and Prometheus for metrics (FastAPI instrumentation).
- **Frontend Work**: Integrate Sentry for frontend error tracking.
- **Database Work**: None
- **AI Work**: Track LLM token usage and latency metrics.
- **Testing Requirements**: Load testing (Locust) to verify SLA targets (p95 response < 200ms).

---

## Completion Checklist

Use this checklist to track the implementation status of the ATS roadmap.

### Platform & Infrastructure
- [x] Scaffold FastAPI backend, Next.js frontend, and Docker-based development environment.
- [x] Configure async SQLAlchemy, Alembic, and core application settings.
- [x] Set up Celery, Redis, logging, and background job infrastructure.

### Authentication & Security
- [x] Implement organization and user models.
- [x] Implement registration, login, refresh, logout, and password reset flows.
- [x] Add role-based access control for protected endpoints.

### ATS Core Data & Workflows
- [x] Create job, candidate, and application models.
- [x] Add candidate CRUD and application management APIs.
- [x] Build candidate portal and recruiter-facing endpoints.

### Resume Intelligence
- [x] Add resume upload validation and storage handling.
- [x] Add parsing logic for extracted candidate details.
- [x] Add background processing for resume parsing tasks.

### Search & Ranking
- [x] Add embedding generation and semantic matching services.
- [x] Add candidate-to-job and candidate-to-candidate similarity search flows.
- [x] Implement configurable business rules for screening.
- [x] Implement feature extraction and ranking model integration.
- [x] Add explainable AI result generation and recruiter-facing insights.

### Recruiter Experience
- [x] Build recruiter dashboard widgets and analytics summaries.
- [x] Build candidate detail page with score, timeline, notes, and actions.
- [x] Implement resume viewer with metadata and highlighting.
- [x] Implement candidate comparison experience.
- [x] Implement hiring workflow and Kanban board transitions.
- [x] Implement interview scheduling and feedback flows.
- [x] Implement recruiter notes and candidate tagging.

### Communication & Reporting
- [x] Implement notification service with email and in-app delivery.
- [x] Implement email template management.
- [x] Implement real-time WebSocket updates.
- [x] Implement reporting and scheduled exports.

### Validation
- [ ] Add end-to-end tests for hiring workflow and candidate ranking.
- [ ] Add UI tests for recruiter dashboard and Kanban interactions.
- [x] Add documentation for deployment, configuration, and operational monitoring.

---

## Implementation Progress

## Implementation Progress

### Completed Sprints ✅
- [x] Platform & Infrastructure (FastAPI, SQLAlchemy, Docker, Celery)
- [x] Authentication & Security (JWT, RBAC, organizations)
- [x] ATS Core Data & Workflows (jobs, candidates, applications)
- [x] Resume Intelligence (upload, parsing, background tasks)
- [x] Search & Ranking Foundations (embeddings, semantic matching)
- [x] Business Rules Engine (configurable screening rules)
- [x] Feature Engineering (ML feature extraction)
- [x] AI Ranking (match score calculation and ranking)
- [x] Explainable AI (insights, recommendations, next steps)
- [x] Recruiter Features Phase 1 (tags, notes, versions)

### In Progress 🔄
- [ ] End-to-end tests (hiring workflow + candidate ranking)
- [ ] UI tests (recruiter dashboard + Kanban)

### Planned 📋
- [ ] Real LLM embedding model integration (OpenAI / HuggingFace)
- [ ] OCR support for scanned resumes
- [ ] Advanced NLP for skill extraction
- [ ] Candidate portal (self-service)

---

## Latest Git Commits

Recent implementation includes:
- fix: remove duplicate getToken declaration in candidate detail page
- feat: add email template management UI with CRUD + variable preview
- feat: add real-time WebSocket notification hook with auto-reconnect
- feat: add WebSocketProvider to dashboard layout for live notifications
- feat: add Email Templates to sidebar navigation
- feat: add interview management module
- feat: add dashboard aggregation endpoints
- feat: add recruiter features (tags and notes)
- feat: add explainable AI insights for candidate-job matches
- feat: add feature extraction and AI ranking engine
- feat: add configurable business rules engine for candidate screening
