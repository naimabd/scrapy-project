from workplace_relations_pipeline.config.models import MetadataRecord


def test_metadata_record_to_dict_has_ingested_at():
    r = MetadataRecord(
        source_body="body",
        source_url="http://example.com",
        identifier="id",
        title="title",
        description="desc",
        published_date="2024-01-01",
        partition_date="2024-01",
        file_type="pdf",
        storage_bucket="b",
        storage_key="k",
        file_hash="h",
    )
    d = r.to_dict()
    assert d["identifier"] == "id"
    assert d["ingested_at"]
