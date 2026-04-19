from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from pipeline.domain.models import MetadataRecord
from pipeline.infrastructure.mongo_repository import MongoRepository
from pipeline.infrastructure.s3_repository import S3Repository
from pipeline.services.utils import build_record_key, compute_sha256, extension_from_url


class LandingZonePipeline:
    def __init__(
        self,
        mongo_uri: str,
        mongo_db: str,
        mongo_col: str,
        s3_endpoint: str,
        s3_key: str,
        s3_secret: str,
        s3_region: str,
        s3_bucket: str,
    ) -> None:
        self.mongo = MongoRepository(mongo_uri, mongo_db)
        self.store = S3Repository(s3_endpoint, s3_key, s3_secret, s3_region, use_ssl=False)
        self.mongo_col = mongo_col
        self.s3_bucket = s3_bucket

    @classmethod
    def from_crawler(cls, crawler: Any) -> LandingZonePipeline:
        settings = crawler.settings
        return cls(
            mongo_uri=settings.get("MONGO_URI"),
            mongo_db=settings.get("MONGO_DB"),
            mongo_col=settings.get("MONGO_COLLECTION_LANDING"),
            s3_endpoint=settings.get("S3_ENDPOINT_URL"),
            s3_key=settings.get("S3_ACCESS_KEY"),
            s3_secret=settings.get("S3_SECRET_KEY"),
            s3_region=settings.get("S3_REGION"),
            s3_bucket=settings.get("S3_BUCKET_LANDING"),
        )

    def open_spider(self, spider: Any) -> None:
        self.mongo.ensure_indexes(self.mongo_col)
        self.store.ensure_bucket(self.s3_bucket)

    def process_item(self, item: Any, spider: Any) -> Any:
        url = item["detail_url"]
        ext = extension_from_url(url)
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        payload = resp.content
        file_hash = compute_sha256(payload)

        # Simple monthly label for partition
        partition_label = datetime.utcnow().strftime("%Y-%m")
        key = f"landing/{partition_label}/{item['identifier']}{ext}"
        record_key = build_record_key(item["source_body"], item["identifier"], partition_label)

        existing = self.mongo.find_one_by_record_key(self.mongo_col, record_key)
        if existing and existing.get("file_hash") == file_hash:
            return item

        self.store.upload_bytes(
            self.s3_bucket, key, payload, content_type=resp.headers.get("Content-Type")
        )

        record = MetadataRecord(
            source_body=item["source_body"],
            source_url=item.get("source_url", url),
            identifier=item["identifier"],
            title=item.get("title", ""),
            description=item.get("description", ""),
            published_date=item.get("published_date", datetime.utcnow().date().isoformat()),
            partition_date=partition_label,
            file_type=ext.replace(".", "") or "html",
            storage_bucket=self.s3_bucket,
            storage_key=key,
            file_hash=file_hash,
            ingested_at=datetime.utcnow().isoformat(),
            status="ok",
            record_key=record_key,
        )

        self.mongo.upsert_by_record_key(self.mongo_col, record.to_dict())
        return item
