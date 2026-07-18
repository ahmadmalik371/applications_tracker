# DECISIONS.md

# Architecture Decision Records (ADRs)

This file tracks major architectural decisions.

## ADR-001: Modular Monolith vs Microservices
**Date**: 2026-07-15
**Decision**: Start with a Modular Monolith.
**Reasoning**: Premature microservices introduce immense operational overhead (network latency, distributed transactions, complex CI/CD). A modular monolith allows us to enforce strict boundaries using Python modules while keeping deployment simple. We can split modules into microservices later if scaling demands it.

## ADR-002: pgvector vs Dedicated Vector DB
**Date**: 2026-07-15
**Decision**: Use `pgvector` inside PostgreSQL.
**Reasoning**: Managing a separate Pinecone, Milvus, or Qdrant cluster adds significant operational complexity and cost. Since our primary data (Jobs, Candidates, Tenants) already lives in Postgres, `pgvector` allows us to perform single-query vector searches combined with relational filters (e.g., `organization_id`), guaranteeing data consistency and tenant isolation.

## ADR-003: Celery vs FastAPI BackgroundTasks
**Date**: 2026-07-15
**Decision**: Use Celery with Redis broker.
**Reasoning**: FastAPI's `BackgroundTasks` run in the same event loop as the web server. Resume parsing and AI generation are highly CPU/IO bound and take seconds to complete. Running them in FastAPI would block the event loop and degrade API performance. Celery provides distributed workers and retry mechanisms.
