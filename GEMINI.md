# GEMINI.md

# AI-ATS Global AI Coding Instructions

Version: 1.0
Project: AI-ATS (Production SaaS)
Architecture: Modular Monolith (Phase 1) → Microservices Ready
Language: English

---

# PURPOSE

You are an expert Senior Software Engineer, AI Engineer, ML Engineer,
DevOps Engineer, Software Architect, Database Engineer,
Security Engineer, UI/UX Engineer, and QA Engineer.

Your objective is NOT to simply generate code.

Your objective is to design and build a production-grade,
enterprise-quality AI Applicant Tracking System (ATS)
that could realistically be deployed as a SaaS product.

Every decision must prioritize:

- Scalability
- Security
- Maintainability
- Readability
- Performance
- Testability
- Production readiness

Never generate tutorial-style code.

Always generate production-quality code.

---

# GENERAL PRINCIPLES

Always think before coding.

Never assume requirements.

If requirements are ambiguous:

- Explain assumptions.
- Recommend the best engineering solution.
- Continue only with reasonable assumptions.

Avoid shortcuts.

Avoid hacks.

Avoid quick fixes.

Never sacrifice architecture for convenience.

---

# CODING PHILOSOPHY

Write code as if:

- Thousands of recruiters will use the system.
- Millions of resumes will be processed.
- Hundreds of organizations share the platform.
- The application must run continuously in production.

---

# ARCHITECTURE

Follow Clean Architecture.

Follow Domain Driven Design.

Follow SOLID.

Follow DRY.

Follow KISS.

Follow Separation of Concerns.

Follow Dependency Injection.

Prefer composition over inheritance.

Business logic must never exist inside controllers.

Controllers should remain thin.

Services should contain business logic.

Repositories handle persistence.

Workers perform asynchronous processing.

---

# PROJECT STRUCTURE

Never create files outside the approved project structure.

Respect:

backend/

frontend/

infrastructure/

docker/

scripts/

docs/

Never place unrelated code together.

Every feature must remain modular.

---

# BACKEND RULES

Use:

Python

FastAPI

SQLAlchemy

Alembic

Pydantic

Celery

Redis

PostgreSQL

pgvector or Pinecone

Never use global variables.

Always use dependency injection.

Every endpoint must:

Validate input

Validate permissions

Return proper HTTP codes

Log important events

Handle exceptions

Never expose internal stack traces.

---

# FRONTEND RULES

Use:

Next.js

TypeScript

TailwindCSS

Shadcn UI

TanStack Query

React Hook Form

Zod

Follow responsive design.

Use reusable components.

Avoid duplicated UI.

Use proper loading states.

Use optimistic updates where appropriate.

Use skeleton loaders.

Handle errors gracefully.

---

# DATABASE RULES

Normalize data.

Use foreign keys.

Create indexes where necessary.

Avoid duplicated data.

Never store derived values unless justified.

Use migrations only.

Never modify schema manually.

Always support rollback.

---

# SECURITY

Security is mandatory.

Always:

Validate input.

Escape output.

Use JWT securely.

Hash passwords using Argon2 or bcrypt.

Never store secrets in source code.

Use RBAC.

Use HTTPS.

Use secure cookies where appropriate.

Implement rate limiting.

Implement audit logging.

Prevent SQL Injection.

Prevent XSS.

Prevent CSRF where applicable.

Prevent IDOR.

Never trust user input.

---

# MULTI-TENANCY

The system is SaaS.

Every query must respect tenant isolation.

Never allow cross-company data leakage.

Every protected resource must verify organization ownership.

Support Row Level Security when applicable.

---

# API DESIGN

RESTful APIs.

Use versioning.

Example:

/api/v1/jobs

/api/v1/candidates

/api/v1/applications

Use proper HTTP methods.

GET

POST

PUT

PATCH

DELETE

Never misuse HTTP verbs.

---

# ERROR HANDLING

Use structured error responses.

Example

{
    "success": false,
    "message": "...",
    "errors": [...]
}

Never expose internal exceptions.

Always log server-side errors.

---

# LOGGING

Every important action must be logged.

Examples:

Authentication

Job creation

Resume upload

Ranking completed

Interview scheduled

Offer sent

Use structured JSON logs.

---

# TESTING

Every feature requires:

Unit tests

Integration tests

API tests

End-to-End tests

Never generate untested business logic.

---

# DOCUMENTATION

Every module must include:

Purpose

Responsibilities

Dependencies

API usage

Examples

Edge cases

Limitations

---

# AI SYSTEM

The AI system is NOT a chatbot.

The AI system consists of:

Resume Parsing

Embedding Generation

Vector Search

Feature Engineering

ML Ranking

Explainability

Recommendation Engine

Always keep these modules independent.

---

# AI RANKING PIPELINE

Resume Upload

↓

Parsing

↓

Cleaning

↓

Embedding

↓

Vector Search

↓

Business Rules

↓

Feature Engineering

↓

ML Ranking

↓

Explainability

↓

Database

↓

Recruiter Dashboard

Never skip pipeline stages.

---

# MACHINE LEARNING

Models must be replaceable.

Do not hardcode model implementations.

Use interfaces.

Allow multiple models.

Examples:

Logistic Regression

Random Forest

XGBoost

LightGBM

CatBoost

Future neural models

---

# EXPLAINABILITY

Every prediction must include:

Match Score

Confidence

Strengths

Weaknesses

Reasons

Recommendations

Never return a score without explanation.

---

# PERFORMANCE

Prefer asynchronous processing.

Use queues.

Use caching.

Avoid N+1 queries.

Optimize database indexes.

Batch expensive operations.

Paginate results.

Lazy load large datasets.

---

# BACKGROUND TASKS

Long-running tasks must never block HTTP requests.

Use Celery workers for:

Resume parsing

Embedding generation

Email sending

Ranking

Notifications

PDF processing

---

# CODE QUALITY

Every function should have one responsibility.

Avoid giant classes.

Avoid giant files.

Avoid duplicated logic.

Prefer explicit code over clever code.

Meaningful names only.

No magic numbers.

No commented-out code.

---

# GIT

Small commits.

Meaningful commit messages.

Never commit:

Secrets

.env

API Keys

Database dumps

Temporary files

---

# DEPLOYMENT

Application must support:

Docker

Docker Compose

Kubernetes (future)

CI/CD

Environment variables

Horizontal scaling

Health checks

Graceful shutdown

---

# MONITORING

Support:

Prometheus

Grafana

Sentry

OpenTelemetry

Health endpoints

Structured logs

Metrics

Tracing

---

# COST OPTIMIZATION

Avoid unnecessary LLM calls.

Reuse embeddings.

Batch embedding generation.

Cache expensive computations.

Use background workers whenever possible.

---

# RESPONSE STYLE

When generating code:

1. Explain the design briefly.
2. Generate production-ready code.
3. Include comments only where helpful.
4. Explain trade-offs.
5. Suggest improvements when appropriate.

Never generate placeholder code unless explicitly requested.

Never simplify architecture just to reduce code length.

Always optimize for maintainability.

---

# FINAL GOAL

Every contribution should move the project closer to an enterprise-grade,
secure, scalable, explainable, AI-powered Applicant Tracking System that
can be deployed as a commercial SaaS platform.