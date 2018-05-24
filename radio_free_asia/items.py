
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class RFAItem(Item):
    date = Field()
    url = Field()
    category = Field()
    keywords = Field()
    title = Field()
    author = Field()
    text = Field()
    title_latin = Field()
    author_latin = Field()
    text_latin = Field()
