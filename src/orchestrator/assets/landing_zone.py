from dagster import AssetExecutionContext, asset

from orchestrator.partitions import MULTIPARTITIONS
from orchestrator.resources import MongoResource, S3Resource
from pipeline.domain.settings import settings
from pipeline.services.ingestion_service import IngestionService


@asset(
    compute_kind="scrapy",
    group_name="landing",
    partitions_def=MULTIPARTITIONS,
)
def landing_zone(
    context: AssetExecutionContext,
    mongo: MongoResource,
    s3: S3Resource,
) -> None:
    """Extracts raw data for a specific partition (date + body)."""
    # Get values from the multi-partition key
    partition_key = context.partition_key.keys_by_dimension
    target_body = partition_key["body"]

    # Calculate month window bounds
    time_window = context.partition_time_window
    start_date = time_window.start.strftime("%Y-%m-%d")
    
    from datetime import timedelta
    # Dagster partition end time is exclusive
    end_date = (time_window.end - timedelta(days=1)).strftime("%Y-%m-%d")

    # Use Dagster's native context logger so output streams directly to the UI
    logger = context.log
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

    # Run for the whole month
    result = service.run_scrape(
        start_date=start_date,
        end_date=end_date,
        bodies=[target_body_id],
        base_url=settings.source_base_url,
        user_agents=settings.user_agents,
        env_vars=env_vars,
        partition_date=start_date[:7],  # YYYY-MM
    )

    if result.returncode != 0:
        raise Exception(f"Scrapy extraction failed for {target_body} in month {start_date[:7]}")

    context.add_output_metadata(
        metadata={
            "month": start_date[:7],
            "body": target_body,
        }
    )
