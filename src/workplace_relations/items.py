import scrapy


class WorkplaceRecordItem(scrapy.Item):
    source_body = scrapy.Field()
    source_url = scrapy.Field()
    identifier = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    published_date = scrapy.Field()
    detail_url = scrapy.Field()
