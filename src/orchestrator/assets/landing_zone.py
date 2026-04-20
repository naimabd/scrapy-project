from __future__ import annotations

from dagster import asset

from orchestrator.partitions import MULTIPARTITIONS
from orchestrator.resources import MongoResource, S3Resource
from pipeline.domain.settings import settings
from pipeline.infrastructure.logger import get_logger
from pipeline.services.ingestion_service import IngestionService


@asset(
    compute_kind="scrapy",
    group_name="landing",
    partitions_def=MULTIPARTITIONS,
)
def landing_zone(
    context,
    mongo: MongoResource,
    s3: S3Resource,
) -> None:
    """Extracts raw data for a specific partition (date + body)."""
    # Get values from the multi-partition key
    partition_key = context.partition_key.keys_by_dimension
    target_date = partition_key["date"]
    target_body = partition_key["body"]

    logger = get_logger(f"landing_{target_body}_{target_date}", settings.log_level)
    service = IngestionService(logger)

    # We pass the resource config as environment variables for the Scrapy subprocess
    env_vars = {
        "MONGO_URI": mongo.uri,
        "MONGO_DB": mongo.db_name,
        "MONGO_COLLECTION_LANDING": settings.mongo_collection_landing,
        "S3_ENDPOINT_URL": s3.endpoint_url,
        "S3_ACCESS_KEY": s3.access_key,
        "S3_SECRET_KEY": s3.secret_key,
        "S3_REGION": s3.region,
        "S3_BUCKET_LANDING": settings.s3_bucket_landing,
    }

    from orchestrator.partitions import BODY_MAPPING
    target_body_id = BODY_MAPPING.get(target_body, "")

    # Run for a single day (start == end) and a single body ID
    result = service.run_scrape(
        start_date=target_date,
        end_date=target_date,
        bodies=[target_body_id],
        base_url=settings.source_base_url,
        user_agents=settings.user_agents,
        env_vars=env_vars,
    )

    if result.returncode != 0:
        raise Exception(f"Scrapy extraction failed for {target_body} on {target_date}")

    context.add_output_metadata(
        metadata={
            "date": target_date,
            "body": target_body,
            "records_stored": result.stored,
            "records_unchanged": result.unchanged,
            "records_failed": result.failed,
            "records_dropped": result.dropped,
            "pages_scraped": result.pages_scraped,
            "elapsed_seconds": result.elapsed_seconds,
        }
    )
