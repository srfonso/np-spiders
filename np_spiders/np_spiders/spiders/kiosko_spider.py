from langdetect import detect, LangDetectException
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule
from urllib.parse import urlparse

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class KioskoSpider(CrawlSpider):
    name = "kiosko_spider"
    close_down = False

    allowed_domains = ["kiosko.net"]
    start_urls = ["https://es.kiosko.net/"]

    np_xpath = "//div[@class='frontPageImage']/a/@href"
    country_xpath = "//div[@class='co']//a/@href"

    custom_settings = {
        'ITEM_PIPELINES': {}
    }

    rules = {
        Rule(
            LinkExtractor(
                allow=(r'es.kiosko.net/[\w\-/]+/np/.+\.html'), 
                allow_domains=allowed_domains, 
                unique=True
            ), 
            callback='parse_item', 
            follow=True
        ),
        Rule(
            LinkExtractor(
                allow=(r'es.kiosko.net/'),
                deny=(r'/np/'), 
                allow_domains=allowed_domains, 
                unique=True
            ), 
            follow=True
        ),
    }

    def __init__(self, **kwargs):
        super().__init__(self.name, **kwargs)


    def parse_item(self, response):
        np_url = response.xpath(self.np_xpath).get()
        np_country = response.xpath(self.country_xpath).get().replace("/","")
        yield {
            "country": np_country,
            "newspaper": np_url,
            "source_url": response.request.url,
        }

