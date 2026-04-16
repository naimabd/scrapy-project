from datetime import date

from workplace_relations_pipeline.pipeline.partitioning import monthly_partitions


def test_monthly_partitions_basic():
    parts = monthly_partitions(date(2024, 1, 15), date(2024, 3, 10))
    assert len(parts) == 3
    assert parts[0].start_date == date(2024, 1, 15)
    assert parts[0].end_date == date(2024, 1, 31)
    assert parts[-1].start_date == date(2024, 3, 1)
    assert parts[-1].end_date == date(2024, 3, 10)
