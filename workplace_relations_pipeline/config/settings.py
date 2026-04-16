from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppSettings:
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017")
    mongo_db: str = os.getenv("MONGO_DB", "workplace_relations_pipeline")
    mongo_collection_landing: str = os.getenv("MONGO_COLLECTION_LANDING", "landing_metadata")
    mongo_collection_transformed: str = os.getenv("MONGO_COLLECTION_TRANSFORMED", "transformed_metadata")

    s3_endpoint_url: str = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "minio")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "minio123")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_bucket_landing: str = os.getenv("S3_BUCKET_LANDING", "landing-docs")
    s3_bucket_transformed: str = os.getenv("S3_BUCKET_TRANSFORMED", "transformed-docs")
    s3_use_ssl: bool = _as_bool(os.getenv("S3_USE_SSL", "false"))

    source_base_url: str = os.getenv("SOURCE_BASE_URL", "https://www.workplacerelations.ie/en/search/?advance=true")
    scrapy_concurrent_requests: int = int(os.getenv("SCRAPY_CONCURRENT_REQUESTS", "4"))
    scrapy_download_delay: float = float(os.getenv("SCRAPY_DOWNLOAD_DELAY", "0.5"))
    scrapy_retry_times: int = int(os.getenv("SCRAPY_RETRY_TIMES", "4"))
    user_agents: list[str] = os.getenv(
        "USER_AGENTS",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64),Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    ).split(",")

    partition_granularity: str = os.getenv("PARTITION_GRANULARITY", "monthly")
    partition_step_days: int = int(os.getenv("PARTITION_STEP_DAYS", "30"))

    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = AppSettings()
