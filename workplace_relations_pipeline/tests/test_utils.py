from workplace_relations_pipeline.services.utils import build_record_key, compute_sha256


def test_build_record_key():
    assert build_record_key("body", "id-1", "2024-01") == "body|id-1|2024-01"


def test_sha256_stable():
    assert compute_sha256(b"abc") == compute_sha256(b"abc")
    assert compute_sha256(b"abc") != compute_sha256(b"abcd")
