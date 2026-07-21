# PROJECT_REQUIREMENTS.md

# AI-ATS — Project Requirements

Version: 1.0
Status: Active
Last Updated: 2026-07-15

---

## 1. Product Overview

AI-ATS is a production-grade, multi-tenant, AI-powered Applicant Tracking System
designed for deployment as a commercial SaaS platform. The system enables
organizations to manage their entire recruitment lifecycle — from job posting
through candidate ranking, interviewing, and offer management — enhanced by
machine learning models that provide explainable candidate-job matching.

---

## 2. Functional Requirements

### 2.1 Authentication & Authorization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AUTH-001 | Users can register with email and password | P0 |
| FR-AUTH-002 | Users can log in and receive a JWT access token and refresh token | P0 |
| FR-AUTH-003 | Users can log out (token revocation) | P0 |
| FR-AUTH-004 | Password reset via email verification | P0 |
| FR-AUTH-005 | Email verification on registration | P0 |
| FR-AUTH-006 | Multi-factor authentication (TOTP) | P1 |
| FR-AUTH-007 | OAuth2 social login (Google, Microsoft) | P2 |
| FR-AUTH-008 | Session management with configurable expiry | P1 |

### 2.2 Organization Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ORG-001 | Create organization during registration (first user becomes Org Admin) | P0 |
| FR-ORG-002 | Update organization profile (name, logo, industry, size, website) | P0 |
| FR-ORG-003 | Organization settings (timezone, locale, branding) | P1 |
| FR-ORG-004 | Organization-level billing and subscription management | P2 |
| FR-ORG-005 | Organization data export (GDPR compliance) | P1 |

### 2.3 User & Role Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-USER-001 | Org Admin can invite users via email | P0 |
| FR-USER-002 | Assign roles to users within the organization | P0 |
| FR-USER-003 | Users can update their profile | P0 |
| FR-USER-004 | Org Admin can deactivate/reactivate users | P0 |
| FR-USER-005 | Custom role creation with granular permissions | P2 |

**System Roles:**

| Role | Description |
|------|-------------|
| Super Admin | Platform-level administration (system operator) |
| Org Admin | Full control within the organization |
| Recruiter | Manages jobs, candidates, applications, and the recruitment pipeline |
| Hiring Manager | Reviews candidates, provides feedback, approves offers |
| Interviewer | Conducts interviews, submits evaluation feedback |
| Candidate | External role — applies to jobs, tracks application status |

### 2.4 Job Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-JOB-001 | Create job postings with structured fields (title, description, requirements, skills, location, salary range, employment type) | P0 |
| FR-JOB-002 | Job lifecycle management (Draft → Open → Paused → Closed → Archived) | P0 |
| FR-JOB-003 | Assign hiring team to a job (recruiter, hiring manager, interviewers) | P0 |
| FR-JOB-004 | Define required and preferred skills with experience levels | P0 |
| FR-JOB-005 | Job templates for recurring positions | P1 |
| FR-JOB-006 | Job duplication | P1 |
| FR-JOB-007 | Internal vs external job visibility | P1 |
| FR-JOB-008 | Job-level custom screening questions | P1 |
| FR-JOB-009 | Generate job embedding for AI matching upon creation | P0 |

### 2.5 Candidate Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CAND-001 | Create candidate profiles (name, email, phone, location, source) | P0 |
| FR-CAND-002 | Upload resume (PDF, DOCX) — triggers AI parsing pipeline | P0 |
| FR-CAND-003 | Store parsed resume data (skills, experience, education, certifications) | P0 |
| FR-CAND-004 | Candidate search and filtering | P0 |
| FR-CAND-005 | Candidate tagging and notes | P1 |
| FR-CAND-006 | Candidate merge (duplicate detection) | P2 |
| FR-CAND-007 | Candidate source tracking (referral, LinkedIn, job board, direct) | P1 |
| FR-CAND-008 | Candidate communication history | P1 |

### 2.6 Application Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-APP-001 | Apply candidate to a job (create application) | P0 |
| FR-APP-002 | Application pipeline stages (Applied → Screening → Interview → Offer → Hired / Rejected) | P0 |
| FR-APP-003 | Move applications between pipeline stages | P0 |
| FR-APP-004 | Application rejection with reason | P0 |
| FR-APP-005 | Bulk application actions (reject, move stage) | P1 |
| FR-APP-006 | Application activity timeline | P1 |
| FR-APP-007 | Application-level notes and feedback | P0 |

### 2.7 AI Ranking & Matching

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AI-001 | Automatic resume parsing upon upload (extract skills, experience, education, certifications) | P0 |
| FR-AI-002 | Generate candidate embeddings from parsed resume data | P0 |
| FR-AI-003 | Generate job embeddings from job requirements | P0 |
| FR-AI-004 | Vector similarity search to find matching candidates for a job | P0 |
| FR-AI-005 | Business rule filtering (location, visa, experience minimums) | P0 |
| FR-AI-006 | Feature engineering for ML ranking (skill overlap, experience ratio, education match, recency) | P0 |
| FR-AI-007 | ML-based candidate ranking with configurable models | P0 |
| FR-AI-008 | Explainable scoring (match score, confidence, strengths, weaknesses, reasons, recommendations) | P0 |
| FR-AI-009 | Re-rank candidates when job requirements change | P1 |
| FR-AI-010 | Candidate recommendations for open jobs | P2 |

### 2.8 Interview Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-INT-001 | Schedule interviews with date, time, type (phone, video, onsite) | P1 |
| FR-INT-002 | Assign interviewers to interview slots | P1 |
| FR-INT-003 | Interview feedback submission with structured scorecard | P1 |
| FR-INT-004 | Interview calendar integration (Google Calendar, Outlook) | P2 |
| FR-INT-005 | Automated interview reminders | P2 |

### 2.9 Offer Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-OFF-001 | Create offer with compensation details | P1 |
| FR-OFF-002 | Offer approval workflow (Hiring Manager → Org Admin) | P1 |
| FR-OFF-003 | Offer status tracking (Draft → Pending Approval → Sent → Accepted → Declined) | P1 |
| FR-OFF-004 | Offer letter template generation | P2 |

### 2.10 Analytics & Reporting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ANA-001 | Dashboard overview (open jobs, active candidates, pipeline stats) | P1 |
| FR-ANA-002 | Time-to-hire metrics | P1 |
| FR-ANA-003 | Source effectiveness analysis | P2 |
| FR-ANA-004 | Pipeline conversion rates | P1 |
| FR-ANA-005 | AI ranking performance metrics | P2 |
| FR-ANA-006 | Export reports (CSV, PDF) | P2 |

### 2.11 Notifications

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-NOT-001 | In-app notifications for pipeline events | P1 |
| FR-NOT-002 | Email notifications (application received, interview scheduled, offer sent) | P1 |
| FR-NOT-003 | Notification preferences per user | P2 |
| FR-NOT-004 | Webhook support for external integrations | P2 |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-PERF-001 | API response time (p95) | < 200ms |
| NFR-PERF-002 | Resume parsing completion time | < 30s |
| NFR-PERF-003 | Candidate ranking for a job (up to 1000 candidates) | < 60s |
| NFR-PERF-004 | Dashboard page load time | < 2s |
| NFR-PERF-005 | Search query response time | < 500ms |
| NFR-PERF-006 | Concurrent users per organization | 50+ |

### 3.2 Scalability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-SCAL-001 | Organizations supported | 10,000+ |
| NFR-SCAL-002 | Total candidates across platform | 10,000,000+ |
| NFR-SCAL-003 | Concurrent resume processing | 100+ |
| NFR-SCAL-004 | Horizontal scaling support | Required |
| NFR-SCAL-005 | Database sharding readiness | Required |

### 3.3 Security

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-SEC-001 | OWASP Top 10 compliance | Required |
| NFR-SEC-002 | Data encryption at rest (AES-256) | Required |
| NFR-SEC-003 | Data encryption in transit (TLS 1.3) | Required |
| NFR-SEC-004 | Multi-tenant data isolation | Required |
| NFR-SEC-005 | Audit logging for all sensitive operations | Required |
| NFR-SEC-006 | Rate limiting on all public endpoints | Required |
| NFR-SEC-007 | Password hashing (Argon2 / bcrypt) | Required |
| NFR-SEC-008 | RBAC enforcement on every endpoint | Required |

### 3.4 Availability & Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-AVAIL-001 | Uptime SLA | 99.9% |
| NFR-AVAIL-002 | Zero-downtime deployments | Required |
| NFR-AVAIL-003 | Automated health checks | Required |
| NFR-AVAIL-004 | Graceful degradation on AI service failure | Required |
| NFR-AVAIL-005 | Database backup frequency | Every 6 hours |

### 3.5 Compliance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-COMP-001 | GDPR compliance (data export, right to erasure) | Required |
| NFR-COMP-002 | SOC 2 readiness | P2 |
| NFR-COMP-003 | EEO compliance (no discriminatory AI decisions) | Required |
| NFR-COMP-004 | Data retention policies | Required |

### 3.6 Maintainability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-MAINT-001 | Test coverage (backend) | > 80% |
| NFR-MAINT-002 | Test coverage (frontend) | > 70% |
| NFR-MAINT-003 | API documentation (auto-generated OpenAPI) | Required |
| NFR-MAINT-004 | Structured logging (JSON) | Required |
| NFR-MAINT-005 | Observability (metrics, tracing, logging) | Required |

---

## 4. Constraints

| Constraint | Detail |
|-----------|--------|
| Architecture | Modular Monolith (Phase 1), Microservices Ready |
| Backend Language | Python 3.11+ |
| Backend Framework | FastAPI |
| Frontend Framework | Next.js 14+ with TypeScript |
| Database | PostgreSQL 16+ with pgvector |
| Cache | Redis 7+ |
| Task Queue | Celery with Redis broker |
| Containerization | Docker, Docker Compose |
| Orchestration (Future) | Kubernetes |
| CI/CD | GitHub Actions |

---

## 5. Assumptions

1. Each user belongs to exactly one organization.
2. The first user to register creates the organization and becomes Org Admin.
3. Candidates can exist independently of applications (talent pool).
4. A candidate can have multiple applications across different jobs.
5. AI ranking is asynchronous — results are stored and served from the database.
6. The system does not conduct interviews — it manages interview scheduling and feedback.
7. The platform operator (Super Admin) manages infrastructure, not client organizations.
8. File storage (resumes, documents) uses object storage (S3-compatible).

---

## 6. Out of Scope (v1)

- Video interviewing platform
- Payroll integration
- Background check integration
- Career page builder
- Applicant self-service portal (beyond status tracking)
- Mobile native applications
- Real-time collaboration (co-editing)
- Marketplace for third-party integrations
