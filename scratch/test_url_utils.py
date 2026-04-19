from __future__ import annotations
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.pipeline.services.utils import build_search_url

def test_url_builder():
    base = "https://example.com/search/"
    
    # Test full params
    url1 = build_search_url(base, from_date="2024-04-01", to_date="2024-04-30", body="2")
    print(f"Full params: {url1}")
    assert "from=1/4/2024" in url1
    assert "to=30/4/2024" in url1
    assert "body=2" in url1
    assert "decisions=1" in url1

    # Test empty body filter
    url2 = build_search_url(base, from_date="2024-01-01", to_date="2024-01-01", body="")
    print(f"Empty body (filtered): {url2}")
    assert "body=" not in url2

    # Test extra params
    url3 = build_search_url(base, from_date="2024-01-01", to_date="2024-01-01", body="15376", advance="true")
    print(f"Extra params: {url3}")
    assert "advance=true" in url3

    print("\nALL URL TESTS PASSED!")

if __name__ == "__main__":
    test_url_builder()
