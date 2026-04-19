from __future__ import annotations

import hashlib
from datetime import datetime
from urllib.parse import urlencode, urlparse


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_record_key(source_body: str, identifier: str, partition_date: str) -> str:
    return f"{source_body}|{identifier}|{partition_date}"


def extension_from_url(url: str, default: str = ".html") -> str:
    path = urlparse(url).path.lower()
    if ".pdf" in path:
        return ".pdf"
    if ".docx" in path:
        return ".docx"
    if ".doc" in path:
        return ".doc"
    if ".htm" in path or ".html" in path:
        return ".html"
    return default


def build_search_url(
    base_url: str,
    from_date: str | None = None,
    to_date: str | None = None,
    body: str | None = None,
    decisions: str = "1",
    **extra_params,
) -> str:
    """
    Constructs a search URL with filtered, formatted parameters.
    Dates are converted from YYYY-MM-DD to D/M/YYYY.
    """
    params = {"decisions": decisions}

    # Handle date formatting if present
    if from_date:
        dt = datetime.strptime(from_date, "%Y-%m-%d")
        params["from"] = f"{dt.day}/{dt.month}/{dt.year}"
    
    if to_date:
        dt = datetime.strptime(to_date, "%Y-%m-%d")
        params["to"] = f"{dt.day}/{dt.month}/{dt.year}"

    if body:
        params["body"] = body

    # Add any extra params and filter out empty values
    params.update(extra_params)
    filtered_params = {k: v for k, v in params.items() if v is not None and v != ""}

    # Construct the final URL
    clean_base = base_url.split("?")[0]
    query_string = urlencode(filtered_params, safe="/")
    
    return f"{clean_base}?{query_string}"
