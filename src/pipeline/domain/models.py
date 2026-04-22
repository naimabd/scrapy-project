from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MetadataRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source_body: str
    source_url: str
    identifier: str
    title: str
    description: str
    published_date: str
    partition_date: str
    file_type: str
    storage_bucket: str
    storage_key: str
    file_hash: str
    ingested_at: Optional[str] = None  # noqa: UP045
    transformed_at: Optional[str] = None  # noqa: UP045
    status: str = "ok"
    error_reason: Optional[str] = None  # noqa: UP045
    source_identifier: Optional[str] = None  # noqa: UP045
    landing_storage_key: Optional[str] = None  # noqa: UP045
    record_key: Optional[str] = None  # noqa: UP045

    def to_dict(self) -> dict[str, object]:
        data = self.model_dump()
        if not self.ingested_at:
            data["ingested_at"] = datetime.utcnow().isoformat()
        return data
