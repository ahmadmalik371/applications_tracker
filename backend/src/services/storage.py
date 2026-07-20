"""Storage service abstraction with pluggable providers.

Supports local filesystem, S3, and MinIO (S3-compatible). Provider selection
is configuration-driven via STORAGE_PROVIDER setting.

Providers implement a common interface:
    - save(data: bytes, key: str, content_type: str) -> str  (returns URL)
    - get(key: str) -> bytes
    - delete(key: str) -> bool
    - exists(key: str) -> bool
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from src.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class StorageProvider(ABC):
    """Abstract storage provider interface."""

    @abstractmethod
    async def save(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        """Save bytes and return a public/internal URL."""

    @abstractmethod
    async def get(self, key: str) -> bytes:
        """Retrieve bytes by key."""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a file by key."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider."""

    def __init__(self, base_dir: str = "./uploads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        file_path = self.base_dir / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        return f"/uploads/{key}"

    async def get(self, key: str) -> bytes:
        file_path = self.base_dir / key
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {key}")
        return file_path.read_bytes()

    async def delete(self, key: str) -> bool:
        file_path = self.base_dir / key
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    async def exists(self, key: str) -> bool:
        return (self.base_dir / key).exists()


class S3StorageProvider(StorageProvider):
    """S3 / MinIO (S3-compatible) storage provider."""

    def __init__(
        self,
        bucket: str = "",
        region: str = "us-east-1",
        access_key: str = "",
        secret_key: str = "",
        endpoint_url: Optional[str] = None,
    ):
        self.bucket = bucket
        self.region = region
        self._client = None
        try:
            import boto3
            self._client = boto3.client(
                "s3",
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                endpoint_url=endpoint_url or None,
            )
        except ImportError:
            logger.warning("boto3 not installed; S3 provider unavailable")

    async def save(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        if not self._client:
            raise RuntimeError("S3 client not configured")
        self._client.put_object(
            Bucket=self.bucket, Key=key, Body=data, ContentType=content_type
        )
        return f"s3://{self.bucket}/{key}"

    async def get(self, key: str) -> bytes:
        if not self._client:
            raise RuntimeError("S3 client not configured")
        response = self._client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    async def delete(self, key: str) -> bool:
        if not self._client:
            raise RuntimeError("S3 client not configured")
        self._client.delete_object(Bucket=self.bucket, Key=key)
        return True

    async def exists(self, key: str) -> bool:
        if not self._client:
            raise RuntimeError("S3 client not configured")
        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False


def get_storage_provider() -> StorageProvider:
    """Factory that returns the configured storage provider."""
    provider = settings.STORAGE_PROVIDER.lower()
    if provider == "s3" or provider == "minio":
        return S3StorageProvider(
            bucket=settings.STORAGE_S3_BUCKET,
            region=settings.STORAGE_S3_REGION,
            access_key=settings.STORAGE_S3_ACCESS_KEY,
            secret_key=settings.STORAGE_S3_SECRET_KEY,
            endpoint_url=settings.STORAGE_S3_ENDPOINT_URL,
        )
    return LocalStorageProvider(base_dir=settings.UPLOADS_DIR)


storage_provider = get_storage_provider()
