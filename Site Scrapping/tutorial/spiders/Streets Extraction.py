import scrapy
import json

class streets_spider(scrapy.Spider):
    name = "streets_extractor"

    def start_requests(self):
        urls = [
            "https://www.ad.co.il/hood/%D7%91%D7%99%D7%AA-%D7%99%D7%A9%D7%A8%D7%90%D7%9C/jerusalem"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        streets_div = response.css("div.city-streetslist")
        for link in streets_div.css("a"):
            yield ({
	"Street-name" : link.css("a::text").extract()[0]
	}
            )