# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import scrapy
from decimal import Decimal
from scrapy.utils.project import get_project_settings
from peewee import (MySQLDatabase, Model, CharField, DecimalField,
                    PrimaryKeyField, DateField, DateTimeField, IntegerField)


mysql = get_project_settings()['MYSQL']
db = MySQLDatabase(mysql.get('db'), host=mysql.get('host'), user=mysql.get('user'),
                   passwd=mysql.get('passwd'), charset='utf8')


class FreshItem(scrapy.Item):
    name = scrapy.Field()
    sku = scrapy.Field()
    unit = scrapy.Field()
    price = scrapy.Field()
    price_origin = scrapy.Field()
    promotion = scrapy.Field()
    volume = scrapy.Field()
    region = scrapy.Field()
    brand = scrapy.Field()
    source = scrapy.Field()
    category_id = scrapy.Field()
    category_name = scrapy.Field()


class Fresh(Model):
    id = PrimaryKeyField()
    name = CharField(default='')
    sku = CharField(index=True)
    unit = CharField(default='')
    price = DecimalField(default=Decimal(0))
    price_origin = DecimalField(default=Decimal(0))
    promotion = CharField(default='')
    volume = CharField(default='0')
    region = CharField(default='')
    brand = CharField(default='')
    source = IntegerField(index=True)
    category_id = CharField(index=True, null=True)
    category_name = CharField(index=True, default='')
    created_at = DateField(index=True, null=True)
    updated_at = DateTimeField(index=True, null=True)

    class Meta:
        database = db

    @classmethod
    def create_(cls, item):
        source = item['source']
        o, created = cls.get_or_create(source=source, sku=item['sku'], created_at=datetime.date.today())

        o.unit = item['unit']
        o.name = item['name']
        o.price = Decimal(item['price'])
        o.price_origin = Decimal(item['price_origin'])
        o.promotion = item['promotion']
        o.volume = item['volume']
        o.region = item['region']
        o.brand = item['brand']
        o.category_id = item['category_id']
        o.category_name = item['category_name']
        o.updated_at = datetime.datetime.now()
        o.source = source
        o.save()


ITEM_MODEL_MAP = {
    FreshItem: Fresh
}
