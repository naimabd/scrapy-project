from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from workplace_relations_pipeline.config.models import MetadataRecord
from workplace_relations_pipeline.config.settings import AppSettings
from workplace_relations_pipeline.logging_utils.json_logger import get_logger
from workplace_relations_pipeline.pipeline.utils import compute_sha256
from workplace_relations_pipeline.storage.mongo_client import MongoRepository
from workplace_relations_pipeline.storage.object_store import ObjectStore
from workplace_relations_pipeline.transform.html_cleaner import extract_relevant_html


@dataclass
class TransformSummary:
    processed: int = 0
    transformed: int = 0
    copied: int = 0
    failed: int = 0


class TransformationService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.logger = get_logger("transform", settings.log_level)
        self.mongo = MongoRepository(settings.mongo_uri, settings.mongo_db)
        self.store = ObjectStore(
            endpoint_url=settings.s3_endpoint_url,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            region=settings.s3_region,
            use_ssl=settings.s3_use_ssl,
        )
        self.mongo.ensure_indexes(settings.mongo_collection_transformed)
        self.store.ensure_bucket(settings.s3_bucket_transformed)

    def run(self, start_date: str, end_date: str) -> TransformSummary:
        summary = TransformSummary()
        cursor = self.mongo.find_by_date_range(self.settings.mongo_collection_landing, start_date, end_date)

        for doc in cursor:
            summary.processed += 1
            try:
                file_bytes = self.store.download_bytes(doc["storage_bucket"], doc["storage_key"])
                ext = "." + doc.get("file_type", "html").lower()
                target_key = f"transformed/{doc['partition_date']}/{doc['identifier']}{ext}"

                if ext in {".html", ".htm"}:
                    payload = extract_relevant_html(file_bytes)
                    summary.transformed += 1
                else:
                    payload = file_bytes
                    summary.copied += 1

                new_hash = compute_sha256(payload)
                existing = self.mongo.collection(self.settings.mongo_collection_transformed).find_one(
                    {"record_key": doc["record_key"]}
                )
                if existing and existing.get("file_hash") == new_hash:
                    continue

                self.store.upload_bytes(self.settings.s3_bucket_transformed, target_key, payload)

                transformed = MetadataRecord(
                    source_body=doc["source_body"],
                    source_url=doc["source_url"],
                    identifier=doc["identifier"],
                    title=doc.get("title", ""),
                    description=doc.get("description", ""),
                    published_date=doc.get("published_date", ""),
                    partition_date=doc["partition_date"],
                    file_type=doc.get("file_type", "html"),
                    storage_bucket=self.settings.s3_bucket_transformed,
                    storage_key=target_key,
                    file_hash=new_hash,
                    ingested_at=doc.get("ingested_at"),
                    transformed_at=datetime.utcnow().isoformat(),
                    status="ok",
                    source_identifier=doc.get("identifier"),
                    landing_storage_key=doc.get("storage_key"),
                ).to_dict()
                transformed["record_key"] = doc["record_key"]
                self.mongo.upsert_by_record_key(self.settings.mongo_collection_transformed, transformed)
            except Exception as exc:  # pragma: no cover
                summary.failed += 1
                self.logger.error("transform_failed", extra={"extra": {"record_key": doc.get("record_key"), "error": str(exc)}})

        self.logger.info(
            "transform_summary",
            extra={
                "extra": {
                    "processed": summary.processed,
                    "transformed": summary.transformed,
                    "copied": summary.copied,
                    "failed": summary.failed,
                }
            },
        )
        return summary
