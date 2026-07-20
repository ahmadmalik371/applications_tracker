# API Documentation

## Overview

The AI-ATS API is a RESTful API built with FastAPI. All endpoints are prefixed
with `/api/v1`. Authentication uses Bearer JWT tokens.

## Authentication

All protected endpoints require an `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Obtain Tokens

**POST /api/v1/auth/register** — Register a new organization and admin user
```json
// Request
{
  "organization_name": "Acme Corp",
  "email": "admin@acme.com",
  "password": "SecurePass123!",
  "full_name": "Admin User"
}
// Response 201
{
  "access_token": "eyJ...",
  "refresh_token": "abc123..."
}
```

**POST /api/v1/auth/login** — Login with email/password
```json
// Request
{ "email": "admin@acme.com", "password": "SecurePass123!" }
// Response 200
{ "access_token": "eyJ...", "refresh_token": "abc123..." }
```

## Error Responses

All errors follow a consistent structure:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [...]
  }
}
```

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 422 | Request validation failed |
| AUTHENTICATION_FAILED | 401 | Invalid or missing token |
| INSUFFICIENT_PERMISSIONS | 403 | Role not authorized |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded |
| INTERNAL_SERVER_ERROR | 500 | Unexpected error |

## Pagination

List endpoints support pagination via `skip` and `limit` query parameters:

```
GET /api/v1/candidates?skip=0&limit=50
```

- `skip` (default: 0) — Number of records to skip
- `limit` (default: 50, max: 100-500 depending on endpoint) — Maximum records to return

## Filtering

### Candidate Search
```
GET /api/v1/candidates/search/hybrid?q=python+developer&limit=20&semantic_weight=0.6&keyword_weight=0.4
```

### Ranking Filter
```
GET /api/v1/rankings/filter/{job_id}?min_score=50&max_score=90&required_skills=Python&required_skills=FastAPI
```

## Rate Limiting

All endpoints are rate-limited. Response headers:
- `X-RateLimit-Limit` — Maximum requests per window
- `X-RateLimit-Remaining` — Remaining requests in current window
- `Retry-After` — Seconds until reset (on 429 responses)

## Core Endpoints

### Candidates
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/candidates | Create candidate |
| GET | /api/v1/candidates | List candidates |
| GET | /api/v1/candidates/{id} | Get candidate |
| PUT | /api/v1/candidates/{id} | Update candidate |
| DELETE | /api/v1/candidates/{id} | Delete candidate |
| POST | /api/v1/candidates/{id}/upload-resume | Upload resume |

### Jobs
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/candidates/jobs | Create job |
| GET | /api/v1/candidates/jobs | List jobs |
| GET | /api/v1/candidates/jobs/{id} | Get job |

### Rankings
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/rankings/candidates/for-job/{job_id} | Rank candidates for job |
| GET | /api/v1/rankings/jobs/for-candidate/{candidate_id} | Rank jobs for candidate |
| GET | /api/v1/rankings/match-score/{candidate_id}/{job_id} | Match score |
| GET | /api/v1/rankings/explain/{candidate_id}/{job_id} | AI explanation |
| POST | /api/v1/rankings/compare | Compare candidates |

### AI Assistant
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/ai-assistant/search | AI search |
| GET | /api/v1/ai-assistant/summarize/{candidate_id} | Resume summary |
| GET | /api/v1/ai-assistant/analyze-jd/{job_id} | JD analysis |
| POST | /api/v1/ai-assistant/interview-questions | Interview questions |
| GET | /api/v1/ai-assistant/skill-gap/{candidate_id}/{job_id} | Skill gap |

### Super Admin
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/admin/stats | Platform stats |
| GET | /api/v1/admin/plans | SaaS plans |
| GET | /api/v1/admin/feature-flags | Feature flags |
| PUT | /api/v1/admin/feature-flags/{key} | Update flag |

### ML Management
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/ml/models | List models |
| POST | /api/v1/ml/models | Create model |
| POST | /api/v1/ml/models/{id}/deploy | Deploy model |
| POST | /api/v1/ml/models/{id}/rollback | Rollback model |
| POST | /api/v1/ml/feedback | Record feedback |
| GET | /api/v1/ml/bias-reports | Bias reports |

## OpenAPI Spec

Interactive API docs are available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
