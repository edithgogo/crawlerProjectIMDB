# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ImdbItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    rating_value = scrapy.Field()
    rating_count = scrapy.Field()
    title = scrapy.Field()
    year = scrapy.Field()
    writer = scrapy.Field()
    director = scrapy.Field()
    stars = scrapy.Field()

