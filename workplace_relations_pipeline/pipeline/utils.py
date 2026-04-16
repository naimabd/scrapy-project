from __future__ import annotations

import hashlib
from urllib.parse import urlparse


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
