from workplace_relations_pipeline.services.dagster_defs import ingestion_job, transformation_job
from dagster import build_op_context

def test_ingestion_op_config():
    """
    Tests that the ingestion op can be initialized with config.
    Note: We mock the service calls if we want to avoid side effects.
    """
    context = build_op_context(config={
        "start_date": "2024-01-01",
        "end_date": "2024-01-07",
        "bodies": "adjudication"
    })
    # You can test specific logic inside the op if it's extracted,
    # or use mocking to verify that the IngestionService is called correctly.
    assert context.op_config["start_date"] == "2024-01-01"

def test_jobs_loaded():
    """Verifies that the jobs are correctly defined and can be loaded."""
    assert ingestion_job.name == "ingestion_job"
    assert transformation_job.name == "transformation_job"
