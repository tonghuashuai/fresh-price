# coding: utf-8

import scrapy
import json
from ..items import FreshItem
from ..const import FreshSource

'''
多点爬虫
'''


class DmallSpider(scrapy.Spider):
    name = 'dmall'
    host = 'https://appapi.dmall.com/app/'
    headers = {'Cookie': '_digger_uuid=a67bf8018a22211b; cookie_id=1521601952508a67bf; inited=true; updateTime=1520518007000; addr=%E5%8C%97%E4%BA%AC%E5%B8%82%E6%B5%B7%E6%B7%80%E5%8C%BA%E5%BA%B7%E5%81%A5%E5%AE%9D%E7%9B%9B%E5%B9%BF%E5%9C%BA; addrId=; appVersion=3.8.5; areaId=110108; bigdata=; community=%E5%BA%B7%E5%81%A5%E5%AE%9D%E7%9B%9B%E5%B9%BF%E5%9C%BA; lat=40.036456; lng=116.372483; platform=IOS; storeGroup=0-148-1,1-148-1,2-148-1; store_id=148; ticketName=; token=; uuid=6928a6385e8876946849f622ad60bc46042aa787; vender_id=1;',
               'storeGroup': '1-148-1;2-148-1', 'platform': 'IOS', 'storeId': 148, 'venderId': 1}

    def start_requests(self):
        url = '{host}wareCategory/list'.format(host=self.host)
        yield scrapy.Request(url, callback=self.parse_category, headers=self.headers)

    def parse_category(self, response):
        if response.body:
            data = json.loads(response.body)
            stores = data.get('data', {}).get('wareCategory')
            for store in stores:
                category_list = store.get('categoryList')
                for top_category in category_list:
                    for category in top_category.get('childCategoryList', []):
                        yield category

                for top_category in category_list:
                    for category in top_category.get('childCategoryList', []):
                        category_id = category.get('categoryId')
                        url = '{host}search/wareSearch'.format(host=self.host)

                        param = {
                            "sortRule": 0,
                            "globalSelection": False,
                            "pos": 0,
                            "categoryId": str(category_id),
                            "pageNum": 1,
                            "src": 0,
                            "noResultSearch": 0,
                            "from": 1,
                            "erpStoreId": "148",
                            "categoryLevel": 2,
                            "sortKey": 0,
                            "businessCode": 1,
                            "venderId": "1",
                            "categoryType": 1,
                            "sort": 0,
                            "pageSize": 20}

                        yield scrapy.FormRequest(url, callback=self.parse_goods_in_category, headers=self.headers,
                                                 method='POST', formdata={'param': json.dumps(param)},
                                                 meta={'category': {'id': category_id, 'name': category.get('categoryName')}, 'page': 1})

    def parse_goods_in_category(self, response):
        if response.body:
            data = json.loads(response.body).get('data', {})
            product_list = data.get('wareList', [])
            for product in product_list:
                yield product

            for product in product_list:
                sku = product.get('sku')
                print '>>>>>>>>>>>>>>>', sku, response.meta.get('page')
                if sku:
                    body_param = {
                        "sku": str(sku),
                        "lng": 116.372483,
                        "lat": 40.036456000000001,
                        "erpStoreId": "148",
                        "venderId": "1"}

                    url = 'https://detail.dmall.com/app/wareDetail/baseinfo'.format(host=self.host)
                    yield scrapy.FormRequest(url, callback=self.parse_goods_info, method='POST',
                                             formdata={'param': json.dumps(body_param)},
                                             meta=response.meta, headers=self.headers)

            # 翻页
            meta = response.meta
            if meta.get('page') == 1:
                total = data.get('pageInfo', {}).get('total')
                page = total / 20 + int((total % 20) > 0)
                for i in (1, page + 1):
                    meta.update(page=i)
                    param = {
                        "sortRule": 0,
                        "globalSelection": False,
                        "pos": 0,
                        "categoryId": str(meta.get('category').get('id')),
                        "pageNum": i,
                        "src": 0,
                        "noResultSearch": 0,
                        "from": 1,
                        "erpStoreId": "148",
                        "categoryLevel": 2,
                        "sortKey": 0,
                        "businessCode": 1,
                        "venderId": "1",
                        "categoryType": 1,
                        "sort": 0,
                        "pageSize": 20}

                    yield scrapy.FormRequest(response.url, callback=self.parse_goods_in_category, headers=self.headers,
                                             method='POST', formdata={'param': json.dumps(param)}, meta=meta)

    def parse_goods_info(self, response):
        if response.body:
            data = json.loads(response.body).get('data', {})

            unit = ''
            region = ''
            brand = ''
            for d in data.get('introduceList'):
                if d.get('name') == u'规格':
                    unit = d.get('value')

                if d.get('name') == u'产地':
                    region = d.get('value')

                if d.get('name') == u'品牌':
                    brand = d.get('value')

            print unit, region, brand
            yield FreshItem(
                name=data.get('wareName'),
                sku=str(data.get('sku')),
                unit=unit,
                price=data.get('promotionWareVO', {}).get('unitProPrice', 0) / float(100),
                price_origin=data.get('promotionWareVO', {}).get('origPrice', 0) / float(100),
                promotion='',
                volume=0,
                region=region,
                brand=brand,
                source=FreshSource.dmall,
                category_id=response.meta.get('category', {}).get('id'),
                category_name=response.meta.get('category', {}).get('name'),
            )
