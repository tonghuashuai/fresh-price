# coding: utf-8

import scrapy
import json
from ..items import FreshItem
from ..const import FreshSource

'''
每日优鲜爬虫
'''


class MissfreshSpider(scrapy.Spider):
    name = 'missfresh'

    params = '?access_token=WVdTeWZJeW1pc1hQQS9BZWxKZVZIcTlkMWI3aTdHZjFtZnVyYUQ1eXNjdz0=&platform=ios&version=7.6.3&tdk=eyJ0b2tlbklkIjoiRE9oQ2ljMmRiOFEzRkJNVkVrSm1IMGhHMmZhTEZIZ3hRa2RpcG44Y0FUNmQ4bU11ekZUcnZDSHJhZFhqSmJWMXR2ejNBb2h3eHNHb21IaXBNaTNteHc9PSIsIm9zIjoiaU9TIiwicHJvZmlsZVRpbWUiOjQxMiwidmVyc2lvbiI6IjMuMC42In0=&SM_Device_ID=20180319115532ea50b973f6200ea8cc1e9698606be29c0173ace1adc1a4dd&session=&imei=ACB5D189-5B8F-4712-BB66-2FC424EE5484&screen_height=736&screen_width=414&type=0'
    host = 'https://as-vip.missfresh.cn/v3/product/'
    headers = {'x-region': '{"address_code":"110105","station_code":"MRYX|mryx_syqpx", "delivery_type": 1}'}

    def start_requests(self):
        url = '{host}categoryList{params}'.format(host=self.host, params=self.params)
        yield scrapy.Request(url, callback=self.parse_category, headers=self.headers)

    def parse_category(self, response):
        if response.body:
            data = json.loads(response.body)
            category_list = data.get('category_list')
            for category in category_list:
                yield category

            for category in category_list:
                internal_id = category.get('internal_id')
                url = '{host}category/{internal_id}{params}'.format(host=self.host, internal_id=internal_id, params=self.params)
                yield scrapy.Request(url, callback=self.parse_goods_in_category, headers=self.headers,
                                     meta={'category': {'id': internal_id, 'name': category.get('name')}})

    def _get_coupon_exception(self, product_tags):
        coupon_exception = 0
        if product_tags:
            for tag in product_tags:
                if tag.get('name') == u'红包不可用':
                    coupon_exception = 1
                    break

        return coupon_exception

    def _get_sellout_label(self, car_btn_name):
        return {u'到货提醒': '缺货',
                u'明日送达': '今日售罄'}.get(car_btn_name, '')

    def parse_goods_in_category(self, response):
        if response.body:
            product_list = json.loads(response.body).get('products')
            for product in product_list:
                yield product

            for product in product_list:
                sku = product.get('sku')
                if sku:
                    response.meta.update(coupon_exception=self._get_coupon_exception(product.get('product_tags')))
                    response.meta.update(sellout=self._get_sellout_label(product.get('cart_btn_name')))
                    url = '{host}{sku}{params}'.format(host=self.host, sku=sku, params=self.params)
                    yield scrapy.Request(url, callback=self.parse_goods_info, meta=response.meta, headers=self.headers,)

    def parse_goods_info(self, response):
        if response.body:
            data = json.loads(response.body)
            yield FreshItem(
                name=data.get('name'),
                sku=data.get('sku'),
                unit=data.get('unit'),
                price=data.get('vip_price_pro', {}).get('price_down', {}).get('price', 0) / float(100),
                price_origin=data.get('vip_price_pro', {}).get('price_up', {}).get('price', 0) / float(100),
                promotion=data.get('promote_tag'),
                volume=data.get('sales_volume'),
                region=data.get('country'),
                brand=data.get('brand'),
                source=FreshSource.missfresh,
                coupon_exception=response.meta.get('coupon_exception'),
                sellout=response.meta.get('sellout'),
                category_id=response.meta.get('category', {}).get('id'),
                category_name=response.meta.get('category', {}).get('name'),
            )
