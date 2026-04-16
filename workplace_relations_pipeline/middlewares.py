from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RotatingUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        user_agents = getattr(spider, "user_agents", [])
        if user_agents:
            request.headers.setdefault(b"User-Agent", user_agents[hash(request.url) % len(user_agents)].encode("utf-8"))
