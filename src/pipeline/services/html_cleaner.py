from __future__ import annotations

from bs4 import BeautifulSoup


def extract_relevant_html(raw_html: bytes) -> bytes:
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup.select(
        "nav, header, footer, aside, script, style, .menu, .navbar, .breadcrumb, .footer"
    ):
        tag.decompose()

    main = soup.select_one("main") or soup.select_one("article") or soup.body or soup
    cleaned = BeautifulSoup("", "html.parser")
    wrapper = cleaned.new_tag("main")
    wrapper.append(BeautifulSoup(str(main), "html.parser"))
    cleaned.append(wrapper)
    return cleaned.prettify().encode("utf-8")
