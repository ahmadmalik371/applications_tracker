# API_SPEC.md

# AI-ATS REST API Specification (v1)

Version: 1.0
Status: Active
Base Path: `/api/v1`

## Overview

The AI-ATS API follows RESTful principles. It accepts and returns JSON. All endpoints require authentication via JWT unless otherwise specified (e.g., login, registration).

## Conventions

- **Pagination**: Endpoints returning collections support `limit` (default: 20, max: 100) and `offset` (default: 0). Responses wrap items in a `data` array with `total`, `limit`, and `offset` metadata.
- **Sorting**: Supported via `sort_by` (field name) and `order` (`asc` or `desc`).
- **Response Format**:
  - Success: HTTP 2XX. Returns the requested resource(s).
  - Error: HTTP 4XX or 5XX. Returns a standard error object.

### Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "loc": ["body", "email"],
        "msg": "value is not a valid email address"
      }
    ]
  },
  "request_id": "req-12345"
}
```

---

## Endpoints

### 1. Authentication

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| POST   | `/auth/register` | Register a new organization and admin | Public |
| POST   | `/auth/login` | Authenticate user, returns JWT access and refresh tokens | Public |
| POST   | `/auth/refresh` | Obtain a new access token using a refresh token | Public |
| POST   | `/auth/logout` | Revoke tokens | Authenticated |

### 2. Organizations

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| GET    | `/organizations/me` | Get current user's organization profile | Org Admin |
| PATCH  | `/organizations/me` | Update organization settings | Org Admin |

### 3. Users

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| GET    | `/users/me` | Get current user's profile | Any |
| PATCH  | `/users/me` | Update current user's profile | Any |
| GET    | `/users` | List users in the organization | Org Admin |
| POST   | `/users` | Invite a new user to the organization | Org Admin |
| PATCH  | `/users/{id}` | Update a user's role or status | Org Admin |

### 4. Jobs

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| GET    | `/jobs` | List organization jobs | Recruiter+ |
| POST   | `/jobs` | Create a new job posting | Recruiter+ |
| GET    | `/jobs/{id}` | Get job details | Recruiter+ |
| PATCH  | `/jobs/{id}` | Update a job (title, status, description) | Recruiter+ |
| DELETE | `/jobs/{id}` | Archive a job | Recruiter+ |

### 5. Candidates

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| GET    | `/candidates` | List and search candidates | Recruiter+ |
| POST   | `/candidates` | Create a candidate profile | Recruiter+ |
| POST   | `/candidates/{id}/resume` | Upload a resume (triggers async parsing/AI) | Recruiter+ |
| GET    | `/candidates/{id}` | Get candidate details (including parsed data) | Recruiter+ |
| PATCH  | `/candidates/{id}` | Update candidate details | Recruiter+ |

### 6. Applications & AI Ranking

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| GET    | `/jobs/{job_id}/applications` | List applications for a job, optionally sorted by AI score | Recruiter+ |
| POST   | `/jobs/{job_id}/applications` | Apply a candidate to a job | Recruiter+ |
| GET    | `/applications/{id}` | Get specific application details | Recruiter+ |
| PATCH  | `/applications/{id}/stage` | Move application to a new stage | Recruiter+ |
| GET    | `/applications/{id}/ai-explanation` | Get detailed explainability for the candidate's match score | Recruiter+ |

### 7. Interviews

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| GET    | `/applications/{id}/interviews` | List interviews for an application | Recruiter+ |
| POST   | `/applications/{id}/interviews` | Schedule a new interview | Recruiter+ |
| POST   | `/interviews/{id}/feedback` | Submit interviewer scorecard | Interviewer+ |

### 8. Analytics

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| GET    | `/analytics/pipeline` | Get pipeline conversion metrics | Org Admin, Recruiter |
| GET    | `/analytics/time-to-hire` | Get time-to-hire metrics | Org Admin, Recruiter |
