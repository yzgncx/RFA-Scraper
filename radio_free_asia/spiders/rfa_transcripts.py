# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from radio_free_asia.items import RFAItem

class RFA_spider(CrawlSpider):
    name = 'rfa'

    allowed_domains = ['www.rfa.org']
    start_urls = [
       'https://www.rfa.org/uyghur/story_archive/'
    ]

    rules = [
        Rule(LinkExtractor(
            allow=['story_archive\?b_start:int=\d*']),
            follow=True),

        Rule(LinkExtractor(
            allow=['.*-\d{14}\.html.*']),
            callback='parse_page'
            )
    ]

    def parse_page(self, response):
        
        item = RFAItem()
        item['url'] = response.url
        item['date'] = response.selector.xpath('//span[@id="story_date"]/text()').extract()
        item['category'] = response.url.split('/')[-2]
        item['keywords'] = response.selector.xpath('//head/meta[@name="keywords"]/@content').extract()

        yield Request(response.url, callback=self.parse_arabic, meta={'item':item}, dont_filter=True)


    def parse_arabic(self, response):

        item = response.meta['item']
        item['title'] = response.selector.xpath('//title/text()').extract()
        item['author'] = response.selector.xpath('//span[@id="story_byline"]/text()').extract()
        item['text'] = response.selector.xpath('//div[@id="storytext"]/.//p/span/text()').extract()+response.selector.xpath('//div[@id="storytext"]/.//p/text()').extract()

        yield Request(response.url + '?encoding=latin', callback=self.parse_latin, meta={'item':item})

    def parse_latin(self, response):

        item = response.meta['item']
        item['title_latin'] = response.selector.xpath('//title/text()').extract()
        item['author_latin'] = response.selector.xpath('//span[@id="story_byline"]/text()').extract()
        item['text_latin'] = response.selector.xpath('//div[@id="storytext"]/.//p/span/text()').extract()+response.selector.xpath('//div[@id="storytext"]/.//p/text()').extract()
       
        yield item


def foo():
    process = CrawlerProcess()
    process.crawl(RFA_spider)
    process.start()
