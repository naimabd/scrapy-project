from __future__ import annotations

from dagster import Definitions, EnvVar, load_assets_from_modules
from orchestrator.assets import landing_zone, processed_zone
from orchestrator.resources import MongoResource, S3Resource

all_assets = load_assets_from_modules([landing_zone, processed_zone])

defs = Definitions(
    assets=all_assets,
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
