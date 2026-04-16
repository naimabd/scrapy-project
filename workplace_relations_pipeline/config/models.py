from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any


@dataclass
class MetadataRecord:
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
    ingested_at: str | None = None
    transformed_at: str | None = None
    status: str = "ok"
    error_reason: str | None = None
    source_identifier: str | None = None
    landing_storage_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if not self.ingested_at:
            payload["ingested_at"] = datetime.utcnow().isoformat()
        return payload
