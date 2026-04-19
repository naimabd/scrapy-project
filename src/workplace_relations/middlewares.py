from __future__ import annotations

import random
from typing import Any


class RotatingUserAgentMiddleware:
    def __init__(self, user_agents: list[str]) -> None:
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler: Any) -> RotatingUserAgentMiddleware:
        # We pass these in via spider arguments or settings
        agents = crawler.settings.get("USER_AGENTS", [])
        return cls(agents)

    def process_request(self, request: Any, spider: Any) -> None:
        if self.user_agents:
            request.headers.setdefault("User-Agent", random.choice(self.user_agents))
