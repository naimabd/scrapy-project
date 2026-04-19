from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from pipeline.domain.models import MetadataRecord
from pipeline.services.html_cleaner import extract_relevant_html
from pipeline.services.utils import compute_sha256

if TYPE_CHECKING:
    from pipeline.infrastructure.mongo_repository import MongoRepository
    from pipeline.infrastructure.s3_repository import S3Repository


@dataclass
class TransformSummary:
    processed: int = 0
    transformed: int = 0
    copied: int = 0
    failed: int = 0


class TransformationService:
    def __init__(
        self,
        mongo: MongoRepository,
        store: S3Repository,
        logger: logging.Logger,
    ) -> None:
        self.mongo = mongo
        self.store = store
        self.logger = logger

    def run(
        self,
        start_date: str,
        end_date: str,
        source_collection: str,
        target_collection: str,
        target_bucket: str,
    ) -> TransformSummary:
        summary = TransformSummary()
        self.mongo.ensure_indexes(target_collection)
        self.store.ensure_bucket(target_bucket)

        cursor = self.mongo.find_by_date_range(source_collection, start_date, end_date)

        for doc in cursor:
            summary.processed += 1
            try:
                file_bytes = self.store.download_bytes(
                    doc["storage_bucket"], doc["storage_key"]
                )
                ext = "." + doc.get("file_type", "html").lower()
                target_key = f"transformed/{doc['partition_date']}/{doc['identifier']}{ext}"

                if ext in {".html", ".htm"}:
                    payload = extract_relevant_html(file_bytes)
                    summary.transformed += 1
                else:
                    payload = file_bytes
                    summary.copied += 1

                new_hash = compute_sha256(payload)
                existing = self.mongo.find_one_by_record_key(
                    target_collection, doc["record_key"]
                )

                if existing and existing.get("file_hash") == new_hash:
                    continue

                self.store.upload_bytes(
                    target_bucket,
                    target_key,
                    payload,
                    content_type="text/html" if ext.startswith(".ht") else None,
                )

                transformed = MetadataRecord(
                    source_body=doc["source_body"],
                    source_url=doc["source_url"],
                    identifier=doc["identifier"],
                    title=doc.get("title", ""),
                    description=doc.get("description", ""),
                    published_date=doc.get("published_date", ""),
                    partition_date=doc["partition_date"],
                    file_type=doc.get("file_type", "html"),
                    storage_bucket=target_bucket,
                    storage_key=target_key,
                    file_hash=new_hash,
                    ingested_at=doc.get("ingested_at"),
                    transformed_at=datetime.utcnow().isoformat(),
                    status="ok",
                    source_identifier=doc.get("identifier"),
                    landing_storage_key=doc.get("storage_key"),
                    record_key=doc["record_key"]
                )
                self.mongo.upsert_by_record_key(target_collection, transformed.to_dict())
            except Exception as exc:
                summary.failed += 1
                self.logger.error(
                    "transform_failed",
                    extra={"extra": {"record_key": doc.get("record_key"), "error": str(exc)}},
                )

        self.logger.info(
            "transform_summary",
            extra={"extra": summary.__dict__},
        )
        return summary
