from __future__ import annotations

from dagster import ConfigurableResource
from src.pipeline.infrastructure.mongo_repository import MongoRepository
from src.pipeline.infrastructure.s3_repository import S3Repository


class MongoResource(ConfigurableResource):
    uri: str
    db_name: str

    def get_client(self) -> MongoRepository:
        return MongoRepository(self.uri, self.db_name)


class S3Resource(ConfigurableResource):
    endpoint_url: str
    access_key: str
    secret_key: str
    region: str
    use_ssl: bool = False

    def get_client(self) -> S3Repository:
        return S3Repository(
            self.endpoint_url,
            self.access_key,
            self.secret_key,
            self.region,
            self.use_ssl,
        )
