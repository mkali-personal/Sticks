import scrapy


class hoods_spider(scrapy.Spider):
    name = "hoods_extractor"

    def start_requests(self):
        urls = [
            "https://www.ad.co.il/city/jerusalem"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        hoods_div = response.css("div.city-hoodlist")
        for link in hoods_div.css("a"):
            yield ({
	link.css("a::text").extract()[0]: link.css("a::attr(href)").extract()[0]
	}
            )