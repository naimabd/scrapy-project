from __future__ import annotations

from datetime import date
from urllib.parse import urljoin

import scrapy

from workplace_relations.items import WorkplaceRecordItem
from src.pipeline.services.utils import build_search_url

class WorkplaceRelationsSpider(scrapy.Spider):
    name = "workplace_relations"

    def __init__(
        self,
        body: str,
        start_date: str,
        end_date: str,
        base_url: str,
        user_agents: str | list[str] | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.body = body
        self.start_date = start_date
        self.end_date = end_date
        self.base_url = base_url
        if isinstance(user_agents, str):
            self.user_agents = [ua.strip() for ua in user_agents.split(",") if ua.strip()]
        else:
            self.user_agents = user_agents or []

    def start_requests(self):

        url = build_search_url(
            base_url=self.base_url,
            from_date=self.start_date,
            to_date=self.end_date,
            body=self.body,
        )
        yield scrapy.Request(
            url=url,
            callback=self.parse_search_page,
            dont_filter=True,
        )

    def parse_search_page(self, response: scrapy.http.Response):
        rows = response.css(".search-results .result-item")
        for row in rows:
            detail_link = row.css("a::attr(href)").get()
            title = (row.css("a::text").get() or "").strip()
            description = (row.css(".description::text").get() or "").strip()
            published_date = (row.css(".date::text").get() or "").strip()
            identifier = (
                row.css(".identifier::text").get()
                or (
                    detail_link.rstrip("/").split("/")[-1]
                    if detail_link
                    else title.replace(" ", "-").lower()
                )
            )
            source_url = urljoin(response.url, detail_link) if detail_link else response.url
            yield WorkplaceRecordItem(
                source_body=self.body,
                source_url=source_url,
                identifier=identifier,
                title=title,
                description=description,
                published_date=published_date or date.today().isoformat(),
                detail_url=source_url,
            )
