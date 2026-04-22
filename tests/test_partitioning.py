from __future__ import annotations
from datetime import date
from src.pipeline.services.partitioning import monthly_partitions

def test_single_month():
    parts = monthly_partitions(date(2024, 1, 1), date(2024, 1, 31))
    assert len(parts) == 1
    assert parts[0].label == "2024-01"
    assert parts[0].start_date == date(2024, 1, 1)
    assert parts[0].end_date == date(2024, 1, 31)

def test_three_months():
    parts = monthly_partitions(date(2024, 1, 1), date(2024, 3, 15))
    assert len(parts) == 3
    assert [p.label for p in parts] == ["2024-01", "2024-02", "2024-03"]
    assert parts[2].end_date == date(2024, 3, 15)

def test_cross_year():
    parts = monthly_partitions(date(2023, 12, 15), date(2024, 1, 5))
    assert len(parts) == 2
    assert parts[0].label == "2023-12"
    assert parts[1].label == "2024-01"
    assert parts[0].start_date == date(2023, 12, 15)
    assert parts[1].end_date == date(2024, 1, 5)

def test_partial_month_boundaries():
    parts = monthly_partitions(date(2024, 1, 10), date(2024, 1, 20))
    assert len(parts) == 1
    assert parts[0].start_date == date(2024, 1, 10)
    assert parts[0].end_date == date(2024, 1, 20)
