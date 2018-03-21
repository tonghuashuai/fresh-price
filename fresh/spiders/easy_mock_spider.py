# coding: utf-8

import scrapy
import json


class EasyMockSpider(scrapy.Spider):
    name = 'easymock'
    host = 'https://easy-mock.com/mock/5ab09b877271f71f4f186b87/'
    headers = {'Accept': 'application/json'}

    def start_requests(self):
        url = '{host}categoryList'.format(host=self.host)
        yield scrapy.Request(url, callback=self.parse_category, headers=self.headers)

    def parse_category(self, response):
        print response.body
        if response.body:
            data = json.loads(response.body)
            category_list = data.get('category_list')
            for category in category_list:
                yield category
