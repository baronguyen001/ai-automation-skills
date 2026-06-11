"""Upload/download artifacts to generic S3-compatible storage.

BYO bucket and credentials through environment variables:
S3_BUCKET, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, optional S3_ENDPOINT_URL,
and optional S3_REGION. The helper prefers boto3 when installed and falls back
to minio when installed. No credentials, bucket names, or endpoints are
hardcoded here.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class S3ConfigError(RuntimeError):
    """Raised when env vars or supported client libraries are missing."""


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if not value:
        raise S3ConfigError(f"missing required env var: {name}")
    return value


def _object_key(path: str | Path, key: str | None = None) -> str:
    return key or Path(path).name


def _boto3_client() -> Any:
    try:
        import boto3  # type: ignore
    except ImportError as exc:
        raise S3ConfigError("install boto3 or minio to use S3 uploads") from exc

    return boto3.client(
        "s3",
        endpoint_url=os.environ.get("S3_ENDPOINT_URL") or None,
        region_name=os.environ.get("S3_REGION", "us-east-1"),
        aws_access_key_id=_env("S3_ACCESS_KEY_ID"),
        aws_secret_access_key=_env("S3_SECRET_ACCESS_KEY"),
    )


def _minio_client() -> Any:
    try:
        from minio import Minio  # type: ignore
    except ImportError as exc:
        raise S3ConfigError("install boto3 or minio to use S3 uploads") from exc

    endpoint = os.environ.get("S3_ENDPOINT_URL", "")
    endpoint = endpoint.removeprefix("https://").removeprefix("http://")
    if not endpoint:
        raise S3ConfigError("S3_ENDPOINT_URL is required when using minio")
    secure = not os.environ.get("S3_ENDPOINT_URL", "").startswith("http://")
    return Minio(
        endpoint,
        access_key=_env("S3_ACCESS_KEY_ID"),
        secret_key=_env("S3_SECRET_ACCESS_KEY"),
        secure=secure,
    )


def upload_file(path: str | Path, key: str | None = None, bucket: str | None = None) -> str:
    """Upload a local file and return the object key."""
    src = Path(path)
    if not src.is_file():
        raise FileNotFoundError(src)
    object_key = _object_key(src, key)
    bucket_name = bucket or _env("S3_BUCKET")

    try:
        client = _boto3_client()
        client.upload_file(str(src), bucket_name, object_key)
    except S3ConfigError:
        client = _minio_client()
        client.fput_object(bucket_name, object_key, str(src))
    return object_key


def download_file(key: str, dest: str | Path, bucket: str | None = None) -> Path:
    """Download an object key to a local path and return that path."""
    out = Path(dest)
    out.parent.mkdir(parents=True, exist_ok=True)
    bucket_name = bucket or _env("S3_BUCKET")

    try:
        client = _boto3_client()
        client.download_file(bucket_name, key, str(out))
    except S3ConfigError:
        client = _minio_client()
        client.fget_object(bucket_name, key, str(out))
    return out


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload/download S3-compatible artifacts")
    sub = parser.add_subparsers(dest="cmd", required=True)
    up = sub.add_parser("upload")
    up.add_argument("path")
    up.add_argument("--key")
    down = sub.add_parser("download")
    down.add_argument("key")
    down.add_argument("dest")
    args = parser.parse_args()

    if args.cmd == "upload":
        print(upload_file(args.path, args.key))
    else:
        print(download_file(args.key, args.dest))
