# -*- coding: utf-8 -*-
__author__ = 'tomek'


import scrapy
from mieszkam.items import MieszkamItem
from urlparse import urlparse, urljoin

class GumtreeSpider(scrapy.Spider):
    name = "gumtree"
    allowed_domains = ["gumtree.pl"]
    start_urls = [
        "http://www.gumtree.pl/fp-mieszkania-i-domy-do-wynajecia/ochota/c9008l3200013"]

    def parse(self, response):
        for item in response.css('.ar-title').xpath('.//a/@href').extract():
            yield scrapy.Request(item, callback=self.parse_item)


        next_page = response.css('.paginationBottomBg').xpath('.//tr/td[1]/a/@href').extract()
        if len(next_page)>0:
            next_page = next_page[0]
            res = urlparse(next_page)
            if(res.scheme==''):
                yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)
            else:
                yield scrapy.Request(next_page, callback=self.parse)

    def parse_item(self, response):
        item = MieszkamItem()
        item["street"] = response.xpath('//td[@itemtype="http://schema.org/Place"]/text()')
        d = {}
        for a in response.css("#attributeTable").xpath(".//tr"):
            d[a.xpath(".//td[1]/text()").extract()[0].strip()] = a.xpath(".//td[2]/text()").extract()[0].strip()
        print d.keys()
        # item["price"] = d["Cena"]
        # item["area"] = d["Wielkość (m2)"]
        # item["rooms"] = d["Liczba pokoi"]