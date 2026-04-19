from __future__ import annotations

from dagster import DailyPartitionsDefinition, MultiPartitionsDefinition, StaticPartitionsDefinition

# Mapping of Legal Body names to their numerical IDs in the URL parameters
BODY_MAPPING = {
    "Employment Appeals Tribunal": "2",
    "Equality Tribunal": "1",
    "Labour Court": "3",
    "Workplace Relations Commission": "15376",
}

# Define the partitions using the human-readable names
BODY_PARTITIONS = StaticPartitionsDefinition(list(BODY_MAPPING.keys()))

# Define the date partitions
DATE_PARTITIONS = DailyPartitionsDefinition(start_date="2024-01-01")

# Combine them into a multi-partition
MULTIPARTITIONS = MultiPartitionsDefinition(
    {
        "date": DATE_PARTITIONS,
        "body": BODY_PARTITIONS,
    }
)
