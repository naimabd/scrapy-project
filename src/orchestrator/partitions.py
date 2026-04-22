from __future__ import annotations

from dagster import (
    MonthlyPartitionsDefinition,
    MultiPartitionsDefinition,
    StaticPartitionsDefinition,
)

# Mapping of Legal Body names to their numerical IDs in the URL parameters
BODY_MAPPING = {
    "Employment Appeals Tribunal": "2",
    "Equality Tribunal": "1",
    "Labour Court": "3",
    "Workplace Relations Commission": "15376",
}

# Define the partitions using the human-readable names
BODY_PARTITIONS = StaticPartitionsDefinition(list(BODY_MAPPING.keys()))

DATE_PARTITIONS = MonthlyPartitionsDefinition(start_date="1900-01-01")

# Combine them into a multi-partition
MULTIPARTITIONS = MultiPartitionsDefinition(
    {
        "date": DATE_PARTITIONS,
        "body": BODY_PARTITIONS,
    }
)
