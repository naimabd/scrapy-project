from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator("user_agents", mode="before")
    @classmethod
    def split_user_agents(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [ua.strip() for ua in v.split(",") if ua.strip()]
        return v

    # MongoDB Settings
    mongo_uri: str = Field(
        default="mongodb://admin:admin@127.0.0.1:27017/?directConnection=true", alias="MONGO_URI"
    )
    mongo_db: str = Field(default="workplace_relations_pipeline", alias="MONGO_DB")
    mongo_collection_landing: str = Field(
        default="landing_metadata", alias="MONGO_COLLECTION_LANDING"
    )
    mongo_collection_transformed: str = Field(
        default="transformed_metadata", alias="MONGO_COLLECTION_TRANSFORMED"
    )

    # S3 Settings
    s3_endpoint_url: str = Field(default="http://localhost:9000", alias="S3_ENDPOINT_URL")
    s3_access_key: str = Field(default="minio", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="minio123", alias="S3_SECRET_KEY")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    s3_bucket_landing: str = Field(default="landing-docs", alias="S3_BUCKET_LANDING")
    s3_bucket_transformed: str = Field(default="transformed-docs", alias="S3_BUCKET_TRANSFORMED")
    s3_use_ssl: bool = Field(default=False, alias="S3_USE_SSL")

    # Scrapy Settings
    source_base_url: str = Field(
        default="https://www.workplacerelations.ie/en/search/", alias="SOURCE_BASE_URL"
    )
    scrapy_concurrent_requests: int = Field(default=4, alias="SCRAPY_CONCURRENT_REQUESTS")
    scrapy_download_delay: float = Field(default=0.5, alias="SCRAPY_DOWNLOAD_DELAY")
    scrapy_retry_times: int = Field(default=4, alias="SCRAPY_RETRY_TIMES")
    user_agents: Any = Field(
        default_factory=lambda: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        ],
        alias="USER_AGENTS",
    )

    # Pipeline Settings
    partition_granularity: str = Field(default="monthly", alias="PARTITION_GRANULARITY")
    partition_step_days: int = Field(default=30, alias="PARTITION_STEP_DAYS")

    # Logging Settings
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


settings = AppSettings()
