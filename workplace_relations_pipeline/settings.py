BOT_NAME = "workplace_relations_pipeline"

SPIDER_MODULES = ["workplace_relations_pipeline.spiders"]
NEWSPIDER_MODULE = "workplace_relations_pipeline.spiders"

ROBOTSTXT_OBEY = False
RETRY_ENABLED = True
HTTPCACHE_ENABLED = False

ITEM_PIPELINES = {}

DOWNLOADER_MIDDLEWARES = {
    "workplace_relations_pipeline.middlewares.RotatingUserAgentMiddleware": 400,
}
