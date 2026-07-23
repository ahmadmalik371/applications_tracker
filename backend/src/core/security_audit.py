"""Security audit and hardening utilities.

Performs runtime security checks, input sanitization, and provides
additional security hardening measures beyond the base implementation.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from fastapi import Request

logger = logging.getLogger(__name__)

# SSRF protection: block requests to internal/private IPs
PRIVATE_IP_PATTERNS = re.compile(
    r"^(127\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|"
    r"169\.254\.|::1|fc00:|fe80:|localhost|0\.0\.0\.0)",
    re.IGNORECASE,
)

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# SQL injection pattern detection (for additional safety)
SQL_INJECTION_PATTERNS = re.compile(
    r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC|"
    r"EXECUTE|MERGE|TRUNCATE|GRANT|REVOKE)\b)",
    re.IGNORECASE,
)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal and injection."""
    # Remove path separators
    filename = filename.replace("\\", "/").split("/")[-1]
    # Remove null bytes
    filename = filename.replace("\x00", "")
    # Remove any non-printable characters
    filename = re.sub(r"[\x00-\x1f\x7f]", "", filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:250] + "." + ext if ext else name[:255]
    return filename


def validate_file_extension(filename: str) -> bool:
    """Validate that the file extension is allowed."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return f".{ext}" in ALLOWED_EXTENSIONS


def validate_file_size(size: int) -> bool:
    """Validate that the file size is within limits."""
    return 0 < size <= MAX_FILE_SIZE


def is_private_url(url: str) -> bool:
    """Check if a URL points to a private/internal network address."""
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        return bool(PRIVATE_IP_PATTERNS.match(hostname))
    except Exception:
        return True  # Block on parse failure


def sanitize_input(value: str, max_length: int = 1000) -> str:
    """Sanitize user input: strip, limit length, remove control chars."""
    if not isinstance(value, str):
        return str(value) if value is not None else ""
    value = value.strip()
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value)
    return value[:max_length]


def detect_sql_injection(value: str) -> bool:
    """Detect potential SQL injection patterns in input."""
    if not isinstance(value, str):
        return False
    return bool(SQL_INJECTION_PATTERNS.search(value))


async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


def create_security_report() -> dict[str, Any]:
    """Generate a security audit report summarizing current posture."""
    return {
        "authentication": {
            "password_hashing": "Argon2id (time_cost=2, memory_cost=102400)",
            "jwt_algorithm": "HS256",
            "access_token_expiry_minutes": 15,
            "refresh_token_expiry_days": 7,
            "mfa_enabled": False,
        },
        "authorization": {
            "rbac_enabled": True,
            "roles": [
                "Super Admin",
                "Company Admin",
                "Recruiter",
                "Hiring Manager",
                "Candidate",
            ],
            "tenant_isolation": "organization_id scoping",
        },
        "rate_limiting": {
            "enabled": True,
            "backend": "Redis with in-memory fallback",
            "scopes": ["auth", "upload", "ai", "search", "reports", "default"],
        },
        "input_validation": {
            "file_extensions": list(ALLOWED_EXTENSIONS),
            "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
            "sql_injection_detection": True,
            "input_sanitization": True,
        },
        "headers": {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        },
        "logging": {
            "structured_json": True,
            "sensitive_data_masking": True,
            "sentry_integration": True,
        },
        "storage": {
            "provider": "pluggable (local/S3/MinIO)",
            "filename_sanitization": True,
        },
        "recommendations": [
            "Enable MFA for admin accounts",
            "Implement API key rotation policy",
            "Add Web Application Firewall (WAF)",
            "Regular penetration testing schedule",
            "Implement certificate pinning for mobile clients",
        ],
    }
