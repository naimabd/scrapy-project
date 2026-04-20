from __future__ import annotations

from typing import Any, Optional

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection


class MongoRepository:
    def __init__(self, uri: str, db_name: str) -> None:
        self.client: MongoClient[dict[str, Any]] = MongoClient(uri)
        self.db = self.client[db_name]

    def collection(self, name: str) -> Collection[dict[str, Any]]:
        return self.db[name]

    def ensure_indexes(self, collection_name: str) -> None:
        col = self.collection(collection_name)
        col.create_index([("record_key", ASCENDING)], unique=True)
        col.create_index([("partition_date", ASCENDING)])
        col.create_index([("published_date", ASCENDING)])

    def upsert_by_record_key(self, collection_name: str, document: dict[str, Any]) -> None:
        col = self.collection(collection_name)
        col.update_one(
            {"record_key": document["record_key"]},
            {"$set": document},
            upsert=True,
        )

    def find_by_date_range(
        self, collection_name: str, start_date: str, end_date: str
    ) -> Any:
        col = self.collection(collection_name)
        return col.find({"published_date": {"$gte": start_date, "$lte": end_date}})

    def find_one_by_record_key(
        self, collection_name: str, record_key: str
    ) -> Optional[dict[str, Any]]:
        col = self.collection(collection_name)
        return col.find_one({"record_key": record_key})
