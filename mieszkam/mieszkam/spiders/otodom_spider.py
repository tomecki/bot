# -*- coding: utf-8 -*-
import re

__author__ = 'tomek'


import scrapy
from mieszkam.items import MieszkamItem
from urlparse import urlparse, urljoin

class OtodomSpider(scrapy.Spider):
    name = "otodom"
    allowed_domains = ["otodom.pl"]
    start_urls = [
        "http://otodom.pl/index.php?mod=listing&source=context&objSearchQuery.OfferType=rent&objSearchQuery.ObjectName=Flat&objSearchQuery.Country.ID=1&objSearchQuery.Province.ID=7&objSearchQuery.District.ID=197&objSearchQuery.CityName=Warszawa&objSearchQuery.Distance=0&objSearchQuery.QuarterName=Ochota&objSearchQuery.StreetName=&objSearchQuery.LatFrom=&objSearchQuery.LatTo=&objSearchQuery.LngFrom=&objSearchQuery.LngTo=&objSearchQuery.PriceFrom=&objSearchQuery.PriceTo=&objSearchQuery.PriceCurrency.ID=1&objSearchQuery.AreaFrom=&objSearchQuery.AreaTo=&objSearchQuery.FlatRoomsNumFrom=&objSearchQuery.FlatRoomsNumTo=&objSearchQuery.FlatFloorFrom=&objSearchQuery.FlatFloorTo=&objSearchQuery.FlatFreeFrom=&objSearchQuery.FlatBuildingType=&objSearchQuery.Heating=&objSearchQuery.BuildingYearFrom=&objSearchQuery.BuildingYearTo=&objSearchQuery.FlatFloorsNoFrom=&objSearchQuery.FlatFloorsNoTo=&objSearchQuery.CreationDate=&objSearchQuery.Description=&objSearchQuery.offerId=&objSearchQuery.Orderby=activation_date%20DESC&resultsPerPage=25&Search=Search&Location=mazowieckie%2C%20Warszawa%2C%20Ochota"]

    def parse(self, response):
        for item in response.css('article').xpath('.//a/@href').extract():
            res = urlparse(item)
            if res.scheme=='':
                yield scrapy.Request(urljoin(response.url, item), callback=self.parse_item)
            else:
                yield scrapy.Request(item, callback=self.parse_item)



        next_page = response.css('.od-pagination .od-pagination_next').xpath('.//@href').extract()
        if len(next_page)>0:
            next_page = next_page[-1]
            res = urlparse(next_page)
            if(res.scheme==''):
                yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)
            else:
                yield scrapy.Request(next_page, callback=self.parse)

    def parse_item(self, response):
        item = MieszkamItem()
        item["price"] = float(re.sub('\D', "", response.css('.od-offer-price').xpath('.//text()').extract()[0].strip()))
        try:
            item["rooms"] = float(re.sub('\D', "", response.css('.od-offer-numbers').xpath('.//tr/td[2]/text()').extract()[0]))
        except:
            item["rooms"] = 1.0
        item["area"] = float(re.sub('\D', "", response.css('.od-offer-area').xpath('.//text()').extract()[0]))
        item["street"] = response.css('.od-offer_map-box_location').xpath('.//text()').extract()[0];
        l = response.css('.od-offer-description-meta').xpath('.//text()').extract()
        for i in range(len(l)):
            if l[i]=="Data dodania: ":
                item["dateadd"] = l[i+1]
            if l[i]=="Data aktualizacji: ":
                item["dateupdate"] = l[i+1]
        item["link"] = str(response.url)
        return item



