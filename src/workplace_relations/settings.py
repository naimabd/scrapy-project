BOT_NAME = "workplace_relations"

SPIDER_MODULES = ["workplace_relations.spiders"]
NEWSPIDER_MODULE = "workplace_relations.spiders"

ROBOTSTXT_OBEY = False
RETRY_ENABLED = True
HTTPCACHE_ENABLED = False

ITEM_PIPELINES = {
    "workplace_relations.pipelines.LandingZonePipeline": 300,
}

DOWNLOADER_MIDDLEWARES = {
    "workplace_relations.middlewares.RotatingUserAgentMiddleware": 400,
}
