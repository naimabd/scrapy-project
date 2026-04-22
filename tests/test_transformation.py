from __future__ import annotations
from unittest.mock import MagicMock, patch
from src.pipeline.services.transformation_service import TransformationService

def test_transformation_service_filtering():
    # Mock repositories
    mongo = MagicMock()
    store = MagicMock()
    logger = MagicMock()
    
    service = TransformationService(mongo, store, logger)
    
    # Setup mock cursor
    mock_cursor = []
    mongo.collection.return_value.find.return_value = mock_cursor
    
    service.run(
        start_date="2024-01-01",
        end_date="2024-01-31",
        source_collection="landing",
        target_collection="transformed",
        target_bucket="bucket",
        partition_date="2024-01",
        source_body="Labour Court"
    )
    
    # Verify that it filtered by BOTH partition_date and source_body
    mongo.collection.return_value.find.assert_called_once_with({
        "partition_date": "2024-01",
        "source_body": "Labour Court"
    })

from src.pipeline.services.html_cleaner import extract_relevant_html

def test_extract_relevant_html_strips_nav_and_footer():
    raw = b"<html><body><nav>Menu</nav><header>Head</header><main>Real Content</main><footer>Foot</footer></body></html>"
    cleaned = extract_relevant_html(raw).decode()
    assert "Menu" not in cleaned
    assert "Head" not in cleaned
    assert "Foot" not in cleaned
    assert "Real Content" in cleaned

def test_extract_relevant_html_strips_scripts():
    raw = b"<html><body><script>alert('bad')</script><main>Content</main></body></html>"
    cleaned = extract_relevant_html(raw).decode()
    assert "alert" not in cleaned
    assert "Content" in cleaned

def test_extract_relevant_html_empty_body():
    raw = b"<html><body></body></html>"
    # Should not raise exception
    cleaned = extract_relevant_html(raw).decode()
    assert "<main>" in cleaned
