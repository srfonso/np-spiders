# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    html = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    lang = scrapy.Field()
    contentLocation = scrapy.Field()
    summary = scrapy.Field()
    keywords = scrapy.Field()
    movies = scrapy.Field()
    top_image = scrapy.Field()
    authors = scrapy.Field()
    topic_list = scrapy.Field()
    publish_date = scrapy.Field()
    is_premium = scrapy.Field() 
    available =  scrapy.Field() 
