# MONITORING.md

# AI-ATS Observability & Monitoring

## 1. Metrics (Prometheus / Grafana)
We export system and business metrics.
- **System**: CPU, Memory, HTTP 5xx rate, HTTP response times (p95, p99).
- **Business**: Resumes parsed per minute, AI API failure rate, Active jobs.

## 2. Tracing (OpenTelemetry)
- Distributed tracing is enabled for all API requests.
- Trace context is propagated from FastAPI -> Celery Worker -> LLM Provider.
- Enables debugging of slow AI responses.

## 3. Error Tracking (Sentry)
- All unhandled exceptions in FastAPI and Celery are sent to Sentry.
- Errors are tagged with `organization_id` and `user_id` (if authenticated).

## 4. Health Checks
- `/api/v1/health`: Checks Postgres and Redis connectivity.
- Used by the load balancer / Kubernetes to route traffic.
