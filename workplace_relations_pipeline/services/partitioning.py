from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class DatePartition:
    start_date: date
    end_date: date

    @property
    def label(self) -> str:
        return self.start_date.strftime("%Y-%m")


def monthly_partitions(start_date: date, end_date: date) -> list[DatePartition]:
    partitions: list[DatePartition] = []
    cursor = date(start_date.year, start_date.month, 1)

    while cursor <= end_date:
        if cursor.month == 12:
            next_month = date(cursor.year + 1, 1, 1)
        else:
            next_month = date(cursor.year, cursor.month + 1, 1)

        part_start = max(start_date, cursor)
        part_end = min(end_date, next_month - timedelta(days=1))
        if part_start <= part_end:
            partitions.append(DatePartition(start_date=part_start, end_date=part_end))
        cursor = next_month

    return partitions
