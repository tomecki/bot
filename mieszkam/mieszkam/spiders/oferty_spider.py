# -*- coding: utf-8 -*-

import scrapy
from mieszkam.items import MieszkamItem
from urlparse import urlparse, urljoin

class OfertySpider(scrapy.Spider):
    name = "oferty"
    allowed_domains = ["oferty.net"]
    start_urls = [
        "http://www.oferty.net/mieszkania/szukaj?ps%5Btype%5D=1&ps%5Blocation%5D%5Btype%5D=4&ps%5Blocation%5D%5Bselect_level0%5D=10&ps%5Blocation%5D%5Bselect_level1%5D=1610&ps%5Blocation%5D%5Bselect_level2%5D=471610&ps%5Blocation%5D%5Bselect_level3%5D%5B0%5D=1400000471610&ps%5Blocation%5D%5Bselect_level4%5D%5B0%5D=0&ps%5Btransaction%5D=2&ps%5Bowner%5D%5B0%5D=1&ps%5Bowner%5D%5B1%5D=4&ps%5Bowner%5D%5B2%5D=2&ps%5Bowner%5D%5B3%5D=128&ps%5Bdate_filter%5D=0&ps%5Bsort_order%5D=price_zero_asc&type=1"]

    def parse(self, response):
        for item in response.xpath('//tr[re:test(@class, "property")]'):
            offer = MieszkamItem()
            print item
            print item.xpath('.//td[re:test(@class, "cell_area")]/text()').extract()
            offer['area'] = item.xpath('.//td[re:test(@class, "cell_area")]/text()').extract()
            offer['price'] = item.xpath('.//td[re:test(@class, "cell_price")]/div/text()').extract()
            offer['rooms'] = item.xpath('.//td[re:test(@class, "cell_rooms")]/text()').extract()
            offer['street'] = item.css('.cell_street').xpath('.//div/text()').extract()
            yield offer

        next_page = response.css("li").css(".navigateNext").xpath('.//a/@href').extract()[0]
        res = urlparse(next_page)
        if(res.scheme==''):
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)
        else:
            yield scrapy.Request(next_page, callback=self.parse)