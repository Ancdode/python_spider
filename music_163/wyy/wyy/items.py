# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WyyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    singer_id = scrapy.Field()
    singer_name = scrapy.Field()
    #music_list = scrapy.Field()
    music_id = scrapy.Field()
    music_name = scrapy.Field()
    music_url = scrapy.Field()
    music_comment_num = scrapy.Field()
    #music_comment_list = scrapy.Field()
    #music_comments = scrapy.Field()
    pass
