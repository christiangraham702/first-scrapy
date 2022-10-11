# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CraigslistItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    description = scrapy.Field()
    long = scrapy.Field()
    latitude = scrapy.Field()
    city = scrapy.Field()
    region = scrapy.Field()
    price = scrapy.Field()
    posting_time = scrapy.Field()


class ListCraigItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    date = scrapy.Field()
    region = scrapy.Field()
    link = scrapy.Field()
    pid = scrapy.Field()
    zip_code = scrapy.Field()
    dist_from_zip = scrapy.Field()


class ListCraigPids(scrapy.Item):
    pid = scrapy.Field()
    link = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    date = scrapy.Field()
    region = scrapy.Field()
