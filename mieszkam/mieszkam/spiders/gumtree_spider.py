# -*- coding: utf-8 -*-
import re

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
            next_page = next_page[-1]
            res = urlparse(next_page)
            if(res.scheme==''):
                yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)
            else:
                yield scrapy.Request(next_page, callback=self.parse)

    def parse_item(self, response):
        item = MieszkamItem()
        item["street"] = response.xpath('//td[@itemtype="http://schema.org/Place"]/text()').extract()[0].strip()
        d = {}
        for a in response.css("#attributeTable").xpath(".//tr"):
            d[a.xpath(".//td[1]/text()").extract()[0].strip()] = a.xpath(".//td[2]/text()").extract()[0].strip()
        if "Cena" in d.keys():
            cena = re.sub(u"Z\u0142 \xa0", "", d["Cena"])
            cena = re.sub("\,", ".", cena)
            try:
                item["price"] = float(re.sub("\s", "", cena))
            except:
                return
        if u"Wielko\u015b\u0107 (m2)" in d.keys():
            item["area"] = float(d[u"Wielko\u015b\u0107 (m2)"])
        if "Liczba pokoi" in d.keys():
            try:
                item["rooms"] = float(re.sub("\D", "", d["Liczba pokoi"]))
            except:
                item["rooms"] = 1.0
        item["link"] = str(response.url)
        if "Ostatnio zmieniony" not in d.keys():
            item["dateadd"] = re.sub('\/', '.', d["Data dodania"])
        else:
            item["dateadd"] = re.sub('\/', '.', d["Data dodania"])
            item["dateupdate"] = re.sub('\/', '.', d["Ostatnio zmieniony"])
        return item