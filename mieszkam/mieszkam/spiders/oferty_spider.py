# -*- coding: utf-8 -*-
import re

__author__ = 'tomek'


import scrapy
from mieszkam.items import MieszkamItem
from urlparse import urlparse, urljoin

class OfertySpider(scrapy.Spider):
    name = "oferty"
    allowed_domains = ["oferty.net"]
    start_urls = [
        "http://www.oferty.net/mieszkania/szukaj?ps%5Blocation%5D%5Btype%5D=1&ps%5Btype%5D=1&ps%5Btransaction%5D=2&ps%5Blocation%5D%5Btext%5D=Warszawa+Ochota"]

    def parse(self, response):
        for item in response.css('.property').xpath('.//a/@href').extract():
            yield scrapy.Request(item, callback=self.parse_item)


        next_page = response.css('.navigateNext').xpath('.//a/@href').extract()
        if len(next_page)>0:
            next_page = next_page[-1]
            res = urlparse(next_page)
            if(res.scheme==''):
                yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)
            else:
                yield scrapy.Request(next_page, callback=self.parse)

    def parse_item(self, response):
        item = MieszkamItem()
        header = response.xpath('//meta[@name="title"]/@content').extract()[0].split(',')
        item["street"] = response.css('.header').xpath('.//h1/text()').extract()[0].split(',')[-1].strip()
        item["price"] = float(re.sub("\D", "", header[-2]))
        item['area'] = float(re.sub("\D", "", header[-3][:-1].strip()))
        d = {}
        l = response.css('.param').xpath('.//dl/*/text()').extract()
        for e in range(len(l)):
            if e%2==0:
                d[l[e].strip()] = ""
            else:
                d[l[e-1].strip()] = l[e].strip()
        # print d
        item["rooms"] = float(d["Liczba pokoi:"])
        item["link"] = str(response.url)
        item["dateadd"] =  re.sub('\-', '.', response.css('.baseParam').xpath('.//div[2]/text()').extract()[0].strip())
        item["dateupdate"] =  re.sub('\-', '.', response.css('.baseParam').xpath('.//div[3]/text()').extract()[0].strip())
        return item



