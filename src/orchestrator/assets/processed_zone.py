from dagster import AssetExecutionContext, asset

from orchestrator.assets.landing_zone import landing_zone
from orchestrator.partitions import MULTIPARTITIONS
from orchestrator.resources import MongoResource, S3Resource
from pipeline.domain.settings import settings
from pipeline.infrastructure.logger import get_logger
from pipeline.services.transformation_service import TransformationService


@asset(
    compute_kind="python",
    group_name="processed",
    deps=[landing_zone],
    partitions_def=MULTIPARTITIONS,
)
def processed_zone(
    context: AssetExecutionContext,
    mongo: MongoResource,
    s3: S3Resource,
) -> None:
    """Cleans and transforms raw data for a specific partition (date + body)."""
    # Get values from the multi-partition key
    partition_key = context.partition_key.keys_by_dimension
    target_date = partition_key["date"]
    target_body = partition_key["body"]
    
    logger = get_logger(f"processed_{target_body}_{target_date}", settings.log_level)

    mongo_client = mongo.get_client()
    s3_client = s3.get_client()

    service = TransformationService(mongo_client, s3_client, logger)

    # Transform data specifically for this one partition (Body + Date)
    try:
        summary = service.run(
            start_date=target_date,
            end_date=target_date,
            source_collection=settings.mongo_collection_landing,
            target_collection=settings.mongo_collection_transformed,
            target_bucket=settings.s3_bucket_transformed,
            partition_date=target_date[:7], # YYYY-MM
            source_body=target_body,
        )
    finally:
        mongo_client.close()

    context.add_output_metadata(
        metadata={
            "processed_count": summary.processed,
            "transformed_count": summary.transformed,
            "failed_count": summary.failed,
            "date": target_date,
        }
    )
