# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import ITEM_MODEL_MAP


class FreshPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLPipeline(object):
    def process_item(self, item, spider):
        cls = ITEM_MODEL_MAP.get(item.__class__)
        if cls:
            if not cls.table_exists():
                cls.create_table()

            cls.create_(item)
