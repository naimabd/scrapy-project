from __future__ import annotations

from dagster import Definitions, job, op, Field, String

from workplace_relations_pipeline.config.settings import settings
from workplace_relations_pipeline.pipeline.ingestion import IngestionService
from workplace_relations_pipeline.pipeline.transformation import TransformationService


@op(
    config_schema={
        "start_date": Field(String),
        "end_date": Field(String),
        "bodies": Field(String, default_value="adjudication,labour-court,employment-appeals-tribunal"),
    }
)
def ingestion_op(context):
    cfg = context.op_config
    svc = IngestionService(settings)
    svc.run(
        start=__import__("datetime").datetime.strptime(cfg["start_date"], "%Y-%m-%d").date(),
        end=__import__("datetime").datetime.strptime(cfg["end_date"], "%Y-%m-%d").date(),
        bodies=[b.strip() for b in cfg["bodies"].split(",") if b.strip()],
    )
    return True


@op(config_schema={"start_date": Field(String), "end_date": Field(String)})
def transformation_op(context, _ingestion_done: bool):
    cfg = context.op_config
    svc = TransformationService(settings)
    svc.run(cfg["start_date"], cfg["end_date"])


@job
def ingestion_job():
    ingestion_op()


@job
def transformation_job():
    transformation_op()


@job
def full_pipeline_job():
    done = ingestion_op()
    transformation_op(done)


defs = Definitions(jobs=[ingestion_job, transformation_job, full_pipeline_job])
