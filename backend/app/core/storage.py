"""
S3 / MinIO storage abstraction.

Provides upload, download, and pre-signed URL generation.
The singleton ``storage_manager`` is constructed lazily so import-time
failures (e.g. MinIO not running) don't crash the module on worker cold-start.
"""
from functools import lru_cache

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import get_settings


class StorageManager:
    """Thin wrapper around a boto3 S3 client."""

    def __init__(self) -> None:
        settings = get_settings()
        self.provider = settings.STORAGE_PROVIDER.lower()

        if self.provider == "minio":
            self.s3 = boto3.client(
                "s3",
                endpoint_url=f"{'https' if settings.MINIO_SECURE else 'http'}://{settings.MINIO_ENDPOINT}",
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                config=Config(signature_version="s3v4"),
                region_name="us-east-1",
            )
            self.bucket = settings.MINIO_BUCKET
        else:
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            self.bucket = settings.S3_BUCKET_NAME

        self._ensure_bucket()

    # ── helpers ──────────────────────────────────────────────────────────

    def _ensure_bucket(self) -> None:
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except ClientError:
            try:
                settings = get_settings()
                if self.provider == "minio" or settings.AWS_REGION == "us-east-1":
                    self.s3.create_bucket(Bucket=self.bucket)
                else:
                    self.s3.create_bucket(
                        Bucket=self.bucket,
                        CreateBucketConfiguration={"LocationConstraint": settings.AWS_REGION},
                    )
            except Exception as exc:
                print(f"[storage] Could not create bucket '{self.bucket}': {exc}")

    # ── public API ───────────────────────────────────────────────────────

    def upload_file_bytes(self, file_bytes: bytes, object_key: str, content_type: str = "image/jpeg") -> str:
        self.s3.put_object(Bucket=self.bucket, Key=object_key, Body=file_bytes, ContentType=content_type)
        return object_key

    def download_file_bytes(self, object_key: str) -> bytes:
        resp = self.s3.get_object(Bucket=self.bucket, Key=object_key)
        return resp["Body"].read()

    def generate_presigned_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        try:
            return self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )
        except ClientError as exc:
            print(f"[storage] presigned GET error: {exc}")
            return ""

    def generate_presigned_upload_url(self, object_key: str, expires_in: int = 3600) -> str:
        try:
            return self.s3.generate_presigned_url(
                "put_object",
                Params={"Bucket": self.bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )
        except ClientError as exc:
            print(f"[storage] presigned PUT error: {exc}")
            return ""

    @staticmethod
    def build_object_key(event_id: str, photographer_id: str, filename: str) -> str:
        """Enforce PRD path schema: events/{event_id}/{photographer_id}/originals/{filename}"""
        return f"events/{event_id}/{photographer_id}/originals/{filename}"


@lru_cache()
def get_storage_manager() -> StorageManager:
    """Lazy singleton — constructed on first call, reused afterwards."""
    return StorageManager()
