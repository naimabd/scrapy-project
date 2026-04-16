from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
import os

import requests
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.utils.project import get_project_settings
from tenacity import retry, stop_after_attempt, wait_exponential

from workplace_relations_pipeline.config.models import MetadataRecord
from workplace_relations_pipeline.config.settings import AppSettings
from workplace_relations_pipeline.logging_utils.json_logger import get_logger
from workplace_relations_pipeline.services.partitioning import monthly_partitions
from workplace_relations_pipeline.services.utils import build_record_key, compute_sha256, extension_from_url
from workplace_relations_pipeline.spiders.workplace_relations_spider import WorkplaceRelationsSpider
from workplace_relations_pipeline.storage.mongo_client import MongoRepository
from workplace_relations_pipeline.storage.object_store import ObjectStore


@dataclass
class IngestionSummary:
    found: int = 0
    stored: int = 0
    failed: int = 0
    skipped_unchanged: int = 0


class IngestionService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.logger = get_logger("ingestion", settings.log_level)
        self.mongo = MongoRepository(settings.mongo_uri, settings.mongo_db)
        self.store = ObjectStore(
            endpoint_url=settings.s3_endpoint_url,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            region=settings.s3_region,
            use_ssl=settings.s3_use_ssl,
        )
        self.mongo.ensure_indexes(settings.mongo_collection_landing)
        self.store.ensure_bucket(settings.s3_bucket_landing)

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=8))
    def _download(self, url: str) -> requests.Response:
        return requests.get(url, timeout=30)

    def _run_partition_scrape(self, body: str, part_start: str, part_end: str) -> list[dict[str, Any]]:
        scraped: list[dict[str, Any]] = []
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "workplace_relations_pipeline.settings")

        scrapy_settings = get_project_settings()
        scrapy_settings.set("CONCURRENT_REQUESTS", self.settings.scrapy_concurrent_requests)
        scrapy_settings.set("DOWNLOAD_DELAY", self.settings.scrapy_download_delay)
        scrapy_settings.set("RETRY_TIMES", self.settings.scrapy_retry_times)

        process = CrawlerProcess(settings=scrapy_settings)
        crawler = process.create_crawler(WorkplaceRelationsSpider)
        crawler.signals.connect(lambda item, response, spider: scraped.append(dict(item)), signal=signals.item_scraped)
        process.crawl(
            crawler,
            body=body,
            start_date=part_start,
            end_date=part_end,
            base_url=self.settings.source_base_url,
            user_agents=self.settings.user_agents,
        )
        process.start(stop_after_crawl=True)
        return scraped

    def run(self, start: date, end: date, bodies: list[str]) -> IngestionSummary:
        summary = IngestionSummary()
        partitions = monthly_partitions(start, end)

        for p in partitions:
            for body in bodies:
                self.logger.info(
                    "partition_start",
                    extra={"extra": {"partition": p.label, "body": body, "start": str(p.start_date), "end": str(p.end_date)}},
                )
                items = self._run_partition_scrape(body, str(p.start_date), str(p.end_date))
                summary.found += len(items)

                for item in items:
                    try:
                        url = item["detail_url"]
                        ext = extension_from_url(url)
                        resp = self._download(url)
                        resp.raise_for_status()
                        payload = resp.content
                        file_hash = compute_sha256(payload)

                        key = f"landing/{p.label}/{item['identifier']}{ext}"
                        record_key = build_record_key(body, item["identifier"], p.label)

                        existing = self.mongo.collection(self.settings.mongo_collection_landing).find_one({"record_key": record_key})
                        if existing and existing.get("file_hash") == file_hash:
                            summary.skipped_unchanged += 1
                            continue

                        ctype = resp.headers.get("Content-Type", "application/octet-stream")
                        self.store.upload_bytes(self.settings.s3_bucket_landing, key, payload, ctype)

                        record = MetadataRecord(
                            source_body=body,
                            source_url=item.get("source_url", url),
                            identifier=item["identifier"],
                            title=item.get("title", ""),
                            description=item.get("description", ""),
                            published_date=item.get("published_date", datetime.utcnow().date().isoformat()),
                            partition_date=p.label,
                            file_type=ext.replace(".", "") or "html",
                            storage_bucket=self.settings.s3_bucket_landing,
                            storage_key=key,
                            file_hash=file_hash,
                            ingested_at=datetime.utcnow().isoformat(),
                            status="ok",
                        ).to_dict()
                        record["record_key"] = record_key
                        self.mongo.upsert_by_record_key(self.settings.mongo_collection_landing, record)
                        summary.stored += 1
                    except Exception as exc:  # pragma: no cover
                        summary.failed += 1
                        self.logger.error(
                            "download_failed",
                            extra={
                                "extra": {
                                    "partition": p.label,
                                    "body": body,
                                    "url": item.get("detail_url"),
                                    "error": str(exc),
                                }
                            },
                        )

                self.logger.info(
                    "partition_end",
                    extra={"extra": {"partition": p.label, "body": body, "found": len(items), "stored": summary.stored, "failed": summary.failed}},
                )

        self.logger.info(
            "run_summary",
            extra={
                "extra": {
                    "found": summary.found,
                    "stored": summary.stored,
                    "failed": summary.failed,
                    "skipped_unchanged": summary.skipped_unchanged,
                }
            },
        )
        return summary
