from __future__ import annotations

import argparse
from datetime import datetime

from workplace_relations_pipeline.config.settings import settings
from workplace_relations_pipeline.pipeline.ingestion import IngestionService
from workplace_relations_pipeline.pipeline.transformation import TransformationService


DEFAULT_BODIES = [
    "adjudication",
    "labour-court",
    "employment-appeals-tribunal",
]


def _date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def run_ingestion() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--bodies", default=",".join(DEFAULT_BODIES))
    args = parser.parse_args()

    svc = IngestionService(settings)
    svc.run(_date(args.start_date), _date(args.end_date), [b.strip() for b in args.bodies.split(",") if b.strip()])


def run_transform() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    args = parser.parse_args()

    svc = TransformationService(settings)
    svc.run(args.start_date, args.end_date)
