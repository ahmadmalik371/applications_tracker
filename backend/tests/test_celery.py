import pytest
from src.core.celery_app import celery_app, debug_task, cleanup_expired_sessions

def test_celery_config():
    """Verify Celery app is initialized and configured correctly."""
    assert celery_app.main == "ai_ats"
    assert celery_app.conf.timezone == "UTC"
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.result_serializer == "json"

def test_celery_tasks():
    """Verify default background tasks are discoverable and run locally (eagerly)."""
    # Use eager mode to execute tasks locally instead of broker
    celery_app.conf.task_always_eager = True
    
    # Run debug task
    result = debug_task.delay()
    assert result.successful()
    assert result.result == "Celery is working!"

    # Run cleanup task
    result_cleanup = cleanup_expired_sessions.delay()
    assert result_cleanup.successful()
    assert result_cleanup.result == "Expired sessions cleaned."
    
    # Reset eager mode
    celery_app.conf.task_always_eager = False
