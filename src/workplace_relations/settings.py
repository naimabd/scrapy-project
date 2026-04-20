import os

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


MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION_LANDING = os.getenv("MONGO_COLLECTION_LANDING")

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_REGION = os.getenv("S3_REGION")
S3_BUCKET_LANDING = os.getenv("S3_BUCKET_LANDING")
