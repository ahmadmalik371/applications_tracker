# DATABASE.md

# AI-ATS Database Schema & Strategy

Version: 1.0
Status: Active

## Overview

AI-ATS uses **PostgreSQL 16+** as its primary relational database. The system utilizes the **pgvector** extension to store and query high-dimensional embeddings for candidates and jobs, enabling AI-powered semantic matching directly within the database alongside traditional relational filtering.

We use **SQLAlchemy** (2.0+) as the ORM and **Alembic** for schema migrations.

---

## Core Principles

1. **Multi-Tenancy**: Almost all tables MUST include an `organization_id` foreign key.
2. **Soft Deletes**: Use `is_active` or `deleted_at` columns instead of hard deleting records, especially for auditing purposes.
3. **Audit Trails**: Critical tables should include `created_at`, `updated_at`, and `created_by` fields.
4. **Referential Integrity**: Always use Foreign Keys with appropriate ON DELETE constraints (typically SET NULL or RESTRICT, rarely CASCADE in a multi-tenant system to prevent accidental massive data loss).
5. **UUIDs**: Use UUIDv4 for primary keys (`id`) to prevent enumeration attacks and simplify distributed data generation.

---

## Schema Overview

### 1. Platform & Tenant Configuration

**`organizations`**
- `id` (UUID, PK)
- `name` (String)
- `domain` (String, Unique)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `is_active` (Boolean)

**`users`**
- `id` (UUID, PK)
- `organization_id` (UUID, FK -> organizations.id, Index)
- `email` (String, Unique per organization)
- `hashed_password` (String)
- `first_name` (String)
- `last_name` (String)
- `role` (Enum: super_admin, org_admin, recruiter, hiring_manager, interviewer)
- `is_active` (Boolean)

### 2. Job Management

**`jobs`**
- `id` (UUID, PK)
- `organization_id` (UUID, FK -> organizations.id, Index)
- `title` (String)
- `description` (Text)
- `status` (Enum: draft, open, paused, closed)
- `location` (String)
- `employment_type` (Enum: full_time, part_time, contract)
- `embedding` (Vector: pgvector, dimensions determined by model)
- `created_by` (UUID, FK -> users.id)
- `created_at` (DateTime)

**`job_skills`** (Join table)
- `job_id` (UUID, FK -> jobs.id)
- `skill_name` (String)
- `is_required` (Boolean)

### 3. Candidate & Applications

**`candidates`**
- `id` (UUID, PK)
- `organization_id` (UUID, FK -> organizations.id, Index)
- `email` (String, Unique per organization)
- `first_name` (String)
- `last_name` (String)
- `resume_url` (String) - S3 URI
- `parsed_data` (JSONB) - Structured resume data (experience, education)
- `embedding` (Vector: pgvector)
- `status` (Enum: processing, ready, failed)
- `created_at` (DateTime)

**`applications`**
- `id` (UUID, PK)
- `organization_id` (UUID, FK -> organizations.id, Index)
- `candidate_id` (UUID, FK -> candidates.id)
- `job_id` (UUID, FK -> jobs.id)
- `stage` (Enum: applied, screening, interview, offer, hired, rejected)
- `rejected_reason` (String, Nullable)
- `match_score` (Float, Nullable) - Latest AI match score for this specific job
- `created_at` (DateTime)

### 4. Interviews & Offers

**`interviews`**
- `id` (UUID, PK)
- `organization_id` (UUID, FK -> organizations.id)
- `application_id` (UUID, FK -> applications.id)
- `scheduled_at` (DateTime)
- `duration_minutes` (Integer)
- `status` (Enum: scheduled, completed, cancelled)

**`interviewers`** (Join table)
- `interview_id` (UUID, FK -> interviews.id)
- `user_id` (UUID, FK -> users.id)
- `score` (Integer, Nullable)
- `feedback` (Text, Nullable)

**`offers`**
- `id` (UUID, PK)
- `organization_id` (UUID, FK -> organizations.id)
- `application_id` (UUID, FK -> applications.id, Unique)
- `salary` (Numeric)
- `status` (Enum: draft, pending_approval, sent, accepted, declined)
- `created_at` (DateTime)

### 5. System & Auditing

**`audit_logs`**
- `id` (UUID, PK)
- `organization_id` (UUID, FK -> organizations.id, Index)
- `user_id` (UUID, FK -> users.id, Nullable)
- `action` (String) - e.g., 'job_created', 'candidate_rejected'
- `resource_type` (String) - e.g., 'job', 'application'
- `resource_id` (UUID)
- `details` (JSONB)
- `ip_address` (String)
- `created_at` (DateTime, Index)

---

## Vector Search (pgvector) Strategy

We use `pgvector` for candidate-to-job matching.

**Indexes**: 
To ensure fast similarity search across millions of candidates, we will use an `HNSW` (Hierarchical Navigable Small World) index on the `embedding` columns.

```sql
CREATE INDEX ON candidates USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON jobs USING hnsw (embedding vector_cosine_ops);
```

**Query Pattern**:
Similarity queries MUST be combined with relational filters (organization ID, business rules) using pre-filtering where possible.

```sql
SELECT id, email, 1 - (embedding <=> :job_embedding) AS similarity_score
FROM candidates
WHERE organization_id = :org_id
AND status = 'ready'
ORDER BY embedding <=> :job_embedding
LIMIT 50;
```

---

## Migrations

- All schema changes MUST be managed via Alembic.
- Manual DDL operations in production are strictly forbidden.
- Migration scripts should include both `upgrade()` and `downgrade()` functions to ensure safe rollbacks.
