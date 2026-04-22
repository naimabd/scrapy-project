from __future__ import annotations

from collections.abc import Generator
from datetime import date, datetime
from urllib.parse import urljoin

import scrapy
from scrapy import Request
from scrapy.http import Response

from pipeline.services.utils import build_search_url
from workplace_relations.items import WorkplaceRecordItem


class WorkplaceRelationsSpider(scrapy.Spider):
    name = "workplace_relations"
    allowed_domains = ["www.workplacerelations.ie"]

    def __init__(
        self,
        body: str,
        start_date: str,
        end_date: str,
        base_url: str,
        partition_date: str | None = None,
        user_agents: str | list[str] | None = None,
        **kwargs: str | None,
    ) -> None:
        super().__init__(**kwargs)
        self.body = body
        self.start_date = start_date
        self.end_date = end_date
        self.base_url = base_url
        self.partition_date = partition_date or date.today().strftime("%Y-%m")
        if isinstance(user_agents, str):
            self.user_agents = [ua.strip() for ua in user_agents.split(",") if ua.strip()]
        else:
            self.user_agents = user_agents or []

    def start_requests(self) -> Generator[Request, None, None]:

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

    def parse_search_page(
        self, response: Response
    ) -> Generator[Request, None, None]:
        rows = response.css("li.each-item.clearfix")
        for row in rows:
            # Try to get the detail link from the 'View Page' button first, then the title
            detail_link = row.css("a.btn.btn-primary::attr(href)").get(
                default=row.css("h2.title a::attr(href)").get(default="")
            )
            title = (row.css("h2.title a::text").get() or "").strip()
            description = (row.css("p.description::text").get() or "").strip()
            raw_date = (row.css("span.date::text").get() or "").strip()
            
            # Normalize date from DD/MM/YYYY to YYYY-MM-DD
            published_date = raw_date
            try:
                if raw_date:
                    dt = datetime.strptime(raw_date, "%d/%m/%Y")
                    published_date = dt.strftime("%Y-%m-%d")
            except Exception:
                pass

            identifier = (
                row.css("span.refNO::text").get()
                or (
                    detail_link.rstrip("/").split("/")[-1]
                    if detail_link
                    else title.replace(" ", "-").lower()
                )
            )
            source_url = urljoin(response.url, detail_link) if detail_link else response.url
            
            item = WorkplaceRecordItem(
                source_body=self.body,
                source_url=source_url,
                identifier=identifier,
                title=title,
                description=description,
                published_date=published_date or date.today().isoformat(),
                detail_url=source_url,
            )

            # Follow the detail link to get the actual content
            yield response.follow(
                source_url,
                callback=self.parse_detail_page,
                meta={"item": item},
            )

        # Follow next page if pagination link is present
        next_href = response.css("a.next::attr(href)").get()
        if next_href:
            yield response.follow(
                next_href,
                callback=self.parse_search_page,
                dont_filter=True,
            )

    def parse_detail_page(
        self, response: Response
    ) -> Generator[WorkplaceRecordItem, None, None]:
        item = response.meta["item"]
        
        # Determine content type
        raw_content_type = response.headers.get("Content-Type")
        if raw_content_type is None:
            content_type = ""
        else:
            content_type = bytes(raw_content_type).decode("utf-8", errors="ignore").lower()
        
        if "application/pdf" in content_type or response.url.lower().endswith(".pdf"):
            item["content_bytes"] = response.body
            item["file_type"] = "pdf"
        elif "msword" in content_type or response.url.lower().endswith((".doc", ".docx")):
            item["content_bytes"] = response.body
            item["file_type"] = response.url.lower().split(".")[-1]
        else:
            # Assume HTML
            item["content_bytes"] = response.body
            item["file_type"] = "html"
            
        yield item

    def closed(self, reason: str) -> None:
        import json
        
        stats_file = self.settings.get("STATS_EXPORT_FILE")
        crawler = self.crawler
        if stats_file and crawler and crawler.stats:
            stats = crawler.stats.get_stats()
            # Convert any non-serializable objects (like datetime) to strings
            safe_stats = {str(k): str(v) for k, v in stats.items()}
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(safe_stats, f)
