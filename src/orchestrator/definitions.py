from __future__ import annotations

from dagster import AssetSelection, Definitions, EnvVar, define_asset_job, load_assets_from_modules

from orchestrator.assets import landing_zone, processed_zone
from orchestrator.resources import MongoResource, S3Resource

all_assets = load_assets_from_modules([landing_zone, processed_zone])

# Job for just scraping
ingestion_job = define_asset_job(
    name="ingestion_job",
    selection=AssetSelection.assets(landing_zone),
    description="Run only the Scrapy ingestion phase.",
)

# Job for just transformation (requires existing landing data)
transformation_job = define_asset_job(
    name="transformation_job",
    selection=AssetSelection.assets(processed_zone),
    description="Run only the BeautifulSoup transformation phase.",
)

# Job for the full end-to-end pipeline
full_pipeline_job = define_asset_job(
    name="full_pipeline_job",
    selection=AssetSelection.all(),
    description="Run the full scrape and transform pipeline.",
)

defs = Definitions(
    assets=all_assets,
    jobs=[ingestion_job, transformation_job, full_pipeline_job],
    resources={
        "mongo": MongoResource(
            uri=EnvVar("MONGO_URI"),
            db_name=EnvVar("MONGO_DB"),
        ),
        "s3": S3Resource(
            endpoint_url=EnvVar("S3_ENDPOINT_URL"),
            access_key=EnvVar("S3_ACCESS_KEY"),
            secret_key=EnvVar("S3_SECRET_KEY"),
            region=EnvVar("S3_REGION"),
            use_ssl=False,
        ),
    },
)
