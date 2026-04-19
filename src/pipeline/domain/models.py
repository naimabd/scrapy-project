from __future__ import annotations

from datetime import datetime
from typing import Any

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
    ingested_at: Optional[str] = None
    transformed_at: Optional[str] = None
    status: str = "ok"
    error_reason: Optional[str] = None
    source_identifier: Optional[str] = None
    landing_storage_key: Optional[str] = None
    record_key: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        if not self.ingested_at:
            data["ingested_at"] = datetime.utcnow().isoformat()
        return data
