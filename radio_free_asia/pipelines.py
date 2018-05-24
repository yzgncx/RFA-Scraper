# -*- coding: utf-8 -*-

from scrapy import signals
from scrapy.exporters import CsvItemExporter
import csv

class RadioFreeAsiaPipeline(object):
    def process_item(self, item, spider):
        return item

class CSVPipeline(object):
    def __init__(self, path):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file = open('%s_items.csv' % spider.name, 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = [
            'date',
            'url',
            'category',
            'keywords',
            'title',
            'author',
            'text',
            'title_latin',
            'author_latin',
            'text_latin',
            ]
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
