from __future__ import annotations

from typing import cast

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]


class S3Repository:
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region: str,
        use_ssl: bool,
    ) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            use_ssl=use_ssl,
        )

    def ensure_bucket(self, bucket: str) -> None:
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError:
            self.client.create_bucket(Bucket=bucket)

    def upload_bytes(
        self, bucket: str, key: str, payload: bytes, content_type: str | None = None
    ) -> None:
        extra: dict[str, str] = {"ContentType": content_type} if content_type else {}
        self.client.put_object(Bucket=bucket, Key=key, Body=payload, **extra)

    def download_bytes(self, bucket: str, key: str) -> bytes:
        res = self.client.get_object(Bucket=bucket, Key=key)
        return res["Body"].read()  # type: ignore

    def copy_object(
        self, source_bucket: str, source_key: str, target_bucket: str, target_key: str
    ) -> None:
        self.client.copy_object(
            CopySource={"Bucket": source_bucket, "Key": source_key},
            Bucket=target_bucket,
            Key=target_key,
        )

    def get_object_hash(self, bucket: str, key: str) -> str | None:
        """Optional: read a custom tag or metadata for the hash."""
        try:
            res = self.client.head_object(Bucket=bucket, Key=key)
            metadata = cast(dict[str, str], res.get("Metadata", {}))
            return metadata.get("file-hash")
        except ClientError:
            return None
