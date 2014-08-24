# -*- coding: utf-8 -*-
import re

__author__ = 'tomek'


import scrapy
from mieszkam.items import MieszkamItem
from urlparse import urlparse, urljoin

class OlxSpider(scrapy.Spider):
    name = "olx"
    allowed_domains = ["olx.pl"]
    start_urls = [
        "http://olx.pl/nieruchomosci/mieszkania/wynajem/warszawa/?search%5Border%5D=created_at%3Adesc&search%5Bdistrict_id%5D=355"]

    def parse(self, response):
        for item in response.css('.offer').css('.link').xpath('.//@href').extract():
            yield scrapy.Request(item, callback=self.parse_item)


        next_page = response.css('.pager .next .link').xpath('.//@href').extract()
        if len(next_page)>0:
            next_page = next_page[-1]
            res = urlparse(next_page)
            if(res.scheme==''):
                yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)
            else:
                yield scrapy.Request(next_page, callback=self.parse)

    def parse_item(self, response):
        item = MieszkamItem()
        item["price"] = float(re.sub("\D", "", response.css('.pricelabel').xpath('.//strong/text()').extract()[0]))
        d = {}
        for el in response.css('.details').xpath('.//td'):
            key = el.xpath('.//div/text()').extract()
            if(len(key)>0):
                value =  el.xpath('.//div/strong/a/text()').extract()
                if(len(value)==0):
                    value =  el.xpath('.//div/strong/text()').extract()
                d[key[0].strip()] = value[0].strip()
        # print d
        item["area"] = float(re.sub("\D", "", d["Powierzchnia:"]))
        try:
            item["rooms"] = float(re.sub("\D", "", d["Liczba pokoi:"]))
        except:
            item["rooms"] = 1.0
        item["link"] = str(response.url)
        return item