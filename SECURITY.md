# SECURITY.md

# AI-ATS Security Policy

## Supported Versions

Currently, only the latest release of AI-ATS is actively supported for security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| 0.x.x   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within AI-ATS, please DO NOT report it publicly (e.g., via GitHub issues). 

Instead, send an email to **security@ai-ats.example.com**. All security vulnerabilities will be promptly addressed.

---

## Security Architecture Guarantees

AI-ATS is a multi-tenant SaaS application handling sensitive Personal Identifiable Information (PII) including resumes, contact details, and hiring data.

### 1. Data Isolation (Multi-Tenancy)
- All tenant data is logically isolated using an `organization_id` column.
- Row-Level Security (RLS) policies or strict Repository-layer filters are enforced on every database query.
- Cross-tenant data access is strictly prohibited and tested via automated CI pipelines.

### 2. Authentication & Authorization
- **Authentication**: JWT (JSON Web Tokens) with short-lived access tokens (15m) and secure, HTTP-only, SameSite refresh cookies.
- **Passwords**: Hashed using Argon2id or bcrypt (cost factor >= 12).
- **Authorization**: Granular Role-Based Access Control (RBAC). Every endpoint explicitly verifies the user's role against the requested resource.

### 3. Data Protection
- **At Rest**: Database volumes and S3 buckets must be encrypted using AES-256.
- **In Transit**: All API traffic MUST be served over TLS 1.3 (HTTPS). Internal service-to-service communication within the cluster should also be encrypted.

### 4. Application Security (OWASP Top 10)
- **Injection**: Prevented via SQLAlchemy ORM. Raw SQL is banned unless absolutely necessary and heavily sanitized.
- **XSS**: Handled natively by React/Next.js escaping. 
- **CSRF**: Mitigated via SameSite cookie attributes and custom headers for API calls.
- **Rate Limiting**: Applied to all endpoints, with aggressive limits on authentication routes.
- **Dependency Scanning**: Enforced in CI via Dependabot/Snyk.

### 5. Audit Logging
- All state-mutating actions (POST, PUT, PATCH, DELETE) and sensitive data access must generate an immutable audit log entry in the `audit_logs` table.
