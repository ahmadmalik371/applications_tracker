"""Prometheus metrics for application monitoring.

Exposes a /metrics endpoint compatible with Prometheus scraping. Tracks:
    - HTTP request latency (histogram)
    - HTTP request count (counter by method/path/status)
    - Active in-flight requests (gauge)
    - Celery task duration (histogram)
    - Celery task count (counter by task name/status)
    - Database connection pool usage (gauge)
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from fastapi import APIRouter, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

try:
    from prometheus_client import (
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        REGISTRY,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
    _HAS_PROMETHEUS = True
except ImportError:
    _HAS_PROMETHEUS = False
    REGISTRY = None

if _HAS_PROMETHEUS:
    REQUEST_COUNT = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "path", "status"],
        registry=REGISTRY,
    )
    REQUEST_LATENCY = Histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "path"],
        registry=REGISTRY,
    )
    INPROGRESS_REQUESTS = Gauge(
        "http_requests_in_progress",
        "In-progress HTTP requests",
        registry=REGISTRY,
    )
    CELERY_TASK_COUNT = Counter(
        "celery_task_total",
        "Total Celery tasks",
        ["task", "status"],
        registry=REGISTRY,
    )
    CELERY_TASK_DURATION = Histogram(
        "celery_task_duration_seconds",
        "Celery task duration in seconds",
        ["task"],
        registry=REGISTRY,
    )
    DB_POOL_USAGE = Gauge(
        "db_pool_connections_in_use",
        "Database connections in use",
        registry=REGISTRY,
    )


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware that records HTTP metrics for Prometheus."""

    async def dispatch(self, request: Request, call_next):
        if not _HAS_PROMETHEUS:
            return await call_next(request)

        if request.url.path == "/metrics":
            return await call_next(request)

        INPROGRESS_REQUESTS.inc()
        start = time.time()
        try:
            response = await call_next(request)
        except Exception:
            REQUEST_COUNT.labels(
                method=request.method,
                path=request.url.path,
                status="500",
            ).inc()
            raise
        finally:
            INPROGRESS_REQUESTS.dec()

        duration = time.time() - start
        REQUEST_LATENCY.labels(
            method=request.method,
            path=request.url.path,
        ).observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            path=request.url.path,
            status=str(response.status_code),
        ).inc()
        return response


def get_metrics_router() -> APIRouter:
    """Returns a router exposing the /metrics endpoint."""
    router = APIRouter(tags=["Monitoring"])

    @router.get("/metrics")
    async def metrics():
        if not _HAS_PROMETHEUS:
            return Response(
                content="prometheus_client not installed",
                media_type="text/plain",
                status_code=503,
            )
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )

    return router
