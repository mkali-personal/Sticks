import scrapy
import json
import urllib
import re

class streets_spider(scrapy.Spider):
    name = "deals_extractor"
    all_hoods_names = ['%D7%A8%D7%9E%D7%95%D7%AA',
 '%D7%A0%D7%95%D7%94-%D7%99%D7%A2%D7%A7%D7%91',
 '%D7%97%D7%95%D7%9E%D7%AA-%D7%A9%D7%9E%D7%95%D7%90%D7%9C%D7%94%D7%A8-%D7%97%D7%95%D7%9E%D7%94',
 '%D7%A4%D7%A1%D7%92%D7%AA-%D7%96%D7%90%D7%91-%D7%9E%D7%96%D7%A8%D7%97',
 '%D7%A8%D7%95%D7%9E%D7%9E%D7%94-%D7%A7-%D7%A6%D7%90%D7%A0%D7%96',
 '%D7%AA%D7%9C%D7%A4%D7%99%D7%95%D7%AA-%D7%9E%D7%96%D7%A8%D7%97',
 '%D7%91%D7%99%D7%AA-%D7%94%D7%9B%D7%A8%D7%9D',
 '%D7%A8%D7%97%D7%91%D7%99%D7%94',
 '%D7%91%D7%99%D7%AA-%D7%95%D7%92%D7%9F',
 '%D7%AA%D7%9C%D7%A4%D7%99%D7%95%D7%AA-%D7%90%D7%A8%D7%A0%D7%95%D7%A0%D7%94',
 '%D7%A7%D7%98%D7%9E%D7%95%D7%9F-%D7%94%D7%99%D7%A9%D7%A0%D7%94',
 '%D7%92%D7%99%D7%9C%D7%94',
 '%D7%A7%D7%98%D7%9E%D7%95%D7%9F-%D7%90-%D7%95',
 '%D7%91%D7%A7%D7%A2%D7%94',
 '%D7%92%D7%91%D7%A2%D7%AA-%D7%9E%D7%A9%D7%95%D7%90%D7%94',
 '%D7%A8%D7%A1%D7%A7%D7%95%D7%92%D7%91%D7%A2%D7%AA-%D7%94%D7%95%D7%A8%D7%93%D7%99%D7%9D',
 '%D7%A4%D7%A1%D7%92%D7%AA-%D7%96%D7%90%D7%91-%D7%9E%D7%A2%D7%A8%D7%91',
 '%D7%A8%D7%9E%D7%AA-%D7%A9%D7%A8%D7%AA',
 '%D7%92%D7%91%D7%A2%D7%AA-%D7%A9%D7%90%D7%95%D7%9C',
 '%D7%A7%D7%A8%D7%99%D7%AA-%D7%9E%D7%A9%D7%94',
 '%D7%A1%D7%A0%D7%94%D7%93%D7%A8%D7%99%D7%94',
 '%D7%A8%D7%9E%D7%95%D7%AA-%D7%90%D7%A9%D7%9B%D7%95%D7%9C',
 '%D7%A2%D7%9E%D7%A7-%D7%A8%D7%A4%D7%90%D7%99%D7%9D',
 '%D7%94%D7%A8-%D7%A0%D7%95%D7%A3',
 '%D7%9E%D7%A7%D7%95%D7%A8-%D7%91%D7%A8%D7%95%D7%9A',
 '%D7%94%D7%92%D7%91%D7%A2%D7%94-%D7%94%D7%A6%D7%A8%D7%A4%D7%AA%D7%99%D7%AA',
 '%D7%A4%D7%A1%D7%92%D7%AA-%D7%96%D7%90%D7%91-%D7%9E%D7%A8%D7%9B%D7%96',
 '%D7%98%D7%9C%D7%91%D7%99%D7%94',
 '%D7%A7%D7%A8%D7%99%D7%AA-%D7%9E%D7%A0%D7%97%D7%9D',
 '%D7%A9%D7%9E%D7%95%D7%90%D7%9C-%D7%94%D7%A0%D7%91%D7%99%D7%90',
 '%D7%92%D7%91%D7%A2%D7%AA-%D7%9E%D7%A8%D7%93%D7%9B%D7%99',
 '%D7%A7%D7%98%D7%9E%D7%95%D7%9F-%D7%97-%D7%98',
 '%D7%9E%D7%97%D7%A0%D7%94-%D7%99%D7%94%D7%95%D7%93%D7%94',
 '%D7%94%D7%91%D7%95%D7%9B%D7%A8%D7%99%D7%9D',
 '%D7%A8%D7%9E%D7%AA-%D7%A9%D7%9C%D7%9E%D7%94',
 '%D7%9E%D7%A2%D7%9C%D7%95%D7%AA-%D7%93%D7%A4%D7%A0%D7%94',
 '%D7%9B%D7%A8%D7%9D-%D7%90%D7%91%D7%A8%D7%94%D7%9D',
 '%D7%9E%D7%A8%D7%9B%D7%96-%D7%94%D7%A2%D7%99%D7%A8',
 '%D7%9E%D7%A0%D7%97%D7%AA',
 '%D7%90%D7%91%D7%95-%D7%98%D7%95%D7%A8',
 '%D7%9E%D7%A7%D7%95%D7%A8-%D7%97%D7%99%D7%99%D7%9D',
 '%D7%A7%D7%A8%D7%99%D7%AA-%D7%94%D7%90%D7%95%D7%9E%D7%94',
 '%D7%A4%D7%A1%D7%92%D7%AA-%D7%96%D7%90%D7%91-%D7%93%D7%A8%D7%95%D7%9D',
 '%D7%A4%D7%AA',
 '%D7%91%D7%99%D7%AA-%D7%99%D7%A9%D7%A8%D7%90%D7%9C',
 '%D7%A0%D7%97%D7%9C%D7%AA-%D7%90%D7%97%D7%99%D7%9D',
 '%D7%A0%D7%95%D7%94-%D7%A9%D7%90%D7%A0%D7%9F',
 '%D7%A4%D7%A1%D7%92%D7%AA-%D7%96%D7%90%D7%91-%D7%A6%D7%A4%D7%95%D7%9F',
 '%D7%A2%D7%99%D7%A8-%D7%92%D7%A0%D7%99%D7%9D',
 '%D7%A2%D7%99%D7%9F-%D7%9B%D7%A8%D7%9D',
 '%D7%9E%D7%90%D7%94-%D7%A9%D7%A2%D7%A8%D7%99%D7%9D',
 '%D7%9E%D7%95%D7%A8%D7%A9%D7%94',
 '%D7%96%D7%9B%D7%A8%D7%95%D7%9F-%D7%9E%D7%A9%D7%94',
 '%D7%9E%D7%9E%D7%99%D7%9C%D7%90',
 '%D7%94%D7%A8%D7%95%D7%91%D7%A2-%D7%94%D7%99%D7%94%D7%95%D7%93%D7%99',
 '%D7%99%D7%9E%D7%99%D7%9F-%D7%9E%D7%A9%D7%94',
 '%D7%92%D7%90%D7%95%D7%9C%D7%94',
 '%D7%90%D7%91%D7%95-%D7%AA%D7%95%D7%A8',
 '%D7%A8%D7%9E%D7%AA-%D7%91%D7%99%D7%AA-%D7%A9%D7%9E%D7%A9-%D7%92',
 '%D7%94%D7%A2%D7%99%D7%A8-%D7%94%D7%A2%D7%AA%D7%99%D7%A7%D7%94-%D7%95%D7%A8%D7%A1%D7%A7%D7%95',
 '%D7%A9%D7%9B%D7%95%D7%A0%D7%94-%D7%91',
 '%D7%A0%D7%95%D7%95%D7%94-%D7%96%D7%90%D7%91',
 '%D7%A9%D7%9B%D7%95%D7%A0%D7%94-%D7%95',
 '%D7%A9%D7%99%D7%9B%D7%95%D7%9F-%D7%93%D7%A8%D7%95%D7%9D',
 '%D7%A9%D7%9B%D7%95%D7%A0%D7%94-%D7%99%D7%90',
 '%D7%A9%D7%97%D7%9E%D7%95%D7%9F',
 '%D7%A2%D7%A8%D7%91%D7%94',
 '%D7%A7%D7%A8%D7%99%D7%AA-%D7%94%D7%99%D7%95%D7%91%D7%9C']

    all_hoods_paths = ["https://www.ad.co.il/nadlanprice?city=jerusalem&hood={}".format(x) for x in all_hoods_names]
    
    def start_requests(self):
        urls = ["https://www.ad.co.il/nadlanprice?city=jerusalem&hood={}".format(x) for x in self.all_hoods_names]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        
        neighborhood = response.url.split('hood=')[1].split('&page')[0]
        
        table = response.xpath('//*[@class="nadlan-sale-table table white table-condensed"]//tbody/tr')
        streets = table .xpath('//td[3]//text()').extract()
        cleaned_streets = [re.sub(r'\d+', '',x).strip() for x in streets]
        distinct_streets = set(cleaned_streets)
        
        for street in distinct_streets:
            yield ({
                    neighborhood : street
                    }
            )
        next_page = response.css('a.nextPage::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)