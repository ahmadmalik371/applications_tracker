# Security Policy

## Overview

The AI-ATS implements defense-in-depth security across authentication, authorization,
multi-tenant isolation, input validation, rate limiting, and secrets management.

## Authentication & Authorization

### Authentication
- **Password hashing**: Argon2id via `argon2-cffi` (time_cost=2, memory_cost=102400, parallelism=8).
- **JWT tokens**: HS256-signed access tokens with configurable expiry (default 30 min).
- **Refresh tokens**: Opaque tokens stored in `refresh_tokens` table with rotation on refresh.
- **Token revocation**: Refresh tokens are revoked on logout and rotated on use.

### Role-Based Access Control (RBAC)
Roles are stored in the `roles` table and linked to users via `role_id`. The `require_role`
dependency enforces role checks at the router level:

| Role | Permissions |
|------|-------------|
| Super Admin | Platform-wide management, all organizations |
| Company Admin | Organization management, all CRUD |
| Recruiter | Candidate/job management, uploads |
| Hiring Manager | Read, interviews, applications |
| Candidate | Self-service only |

### Tenant Isolation
- Every database query is scoped by `organization_id`.
- The `get_current_user` dependency injects the user's `organization_id` into all queries.
- Cross-tenant access is blocked at the query level (WHERE clause on `organization_id`).

## Input Validation & Injection Prevention

### SQL Injection
- All database access uses SQLAlchemy ORM with parameterized queries.
- No raw SQL is used in application code except in migrations (which use Alembic's op API).

### XSS
- Frontend uses React/Next.js with automatic escaping.
- API responses are JSON; no HTML rendering on the backend.

### CSRF
- API uses Bearer token authentication (not cookies), so CSRF is not applicable.
- CORS is configured with explicit allowed origins (not wildcard in production).

### SSRF
- No outbound HTTP requests are made based on user input.
- File uploads are validated by extension and size before storage.

### IDOR
- All resource access checks `organization_id` ownership.
- UUIDs are used as primary keys to prevent enumeration attacks.

## Rate Limiting

Redis-backed rate limiting is enforced via `RateLimitMiddleware`:

| Scope | Limit (req/min) | Paths |
|-------|-----------------|-------|
| Auth | 10 | `/api/v1/auth/*` |
| Upload | 20 | `*upload*` |
| AI | 50 | `/ai-assistant/*`, `/ml/*`, `/recommendations/*` |
| Search | 60 | `*/search*` |
| Reports | 10 | `*/reports/*`, `*/export*` |
| Default | 100 | All other paths |

Rate limit is per client IP. Responses include `X-RateLimit-Limit`, `X-RateLimit-Remaining`,
and `Retry-After` headers. Exceeded limits return HTTP 429.

## Secrets Management

- Secrets are loaded from environment variables via `pydantic-settings`.
- `.env` files are gitignored and never committed.
- `.env.example` documents required variables without real values.
- Sensitive data is masked in structured logs (passwords, tokens, API keys, emails).
- Sentry events are scrubbed of sensitive data via `before_send` hooks.

## File Security

- Resume uploads are validated by extension (`.pdf`, `.doc`, `.docx`, `.txt`).
- Maximum file size: 10MB.
- Files are stored via the pluggable storage abstraction (local/S3/MinIO).
- File names are sanitized and replaced with UUID-based names.

## CORS

- `allow_origins` is configurable via `CORS_ORIGINS` env var (comma-separated).
- In production, wildcard (`*`) is replaced with explicit domain allowlist.
- Allowed methods are restricted to the HTTP verbs used by the API.

## Security Testing

- Unit tests verify RBAC enforcement and tenant isolation.
- Integration tests validate authentication flows.
- Security scan (Bandit) runs in CI pipeline.

## Reporting Vulnerabilities

Please report security vulnerabilities to security@example.com. Do not open
public issues for security-related reports.
