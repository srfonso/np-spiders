import json
import tldextract
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request
from np_spiders.settings import CONF_JSON_PATH, DOWNLOADER_MIDDLEWARES
from np_spiders.utils import extract_schemeorg
from np_spiders.items import NewsItem

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class GeneralSpider(CrawlSpider):
    name="general"

    close_down = False

    #==== Regular expression path (without domain) ====
    # Match only articles (Default format: domain/topic/topic/YYYY/MM/DD/xxxxx.html)
    re_article_list = [r'/[\w\-/]+/\d+/\d+/\d+/.+']
    # Match any page excluding articles (Default format: without /YYYY/MM/DD)
    re_else_list = [r'/[\D/]*[\w\-]+\.html']

    # Custom headers
    custom_headers = None

    def __init__(self, mode="ALL", start_urls=None, **kwargs):
        # Read configuration for this spider
        with open(CONF_JSON_PATH,'r') as file:
            # In case of 
            if self.name == "general":
                mode = None # (forcing any mode)
                config = {} # Not general config
                if not start_urls:
                    raise Exception(
                        f"'{self.name.capitalize()}' scraper only works with a predefined list of urls."
                         " Please, 'start_urls' parameter is required."
                    )
                
                # Create allowed domains for all the urls from any website
                self.allowed_domains = []
                for url in start_urls:
                    extract_result = tldextract.extract(url)
                    self.allowed_domains.append(
                        "{}.{}".format(extract_result.domain, extract_result.suffix)
                    )
                
            else:
                config = json.load(file).get(self.name, {})
                if not config:
                    raise Exception(f"Configuration for {self.name} doesn't exist.")
            
                # Allowed domains from the config file
                self.allowed_domains = config.get("allowed_domains", "")

        # Custom headers
        self.custom_headers = config.get("custom_headers", None)

        # XPATH content
        self.info_xpath = config.get("info_xpath", "//script[@type='application/ld+json']/text()") # Standard scheme.org xpath
        self.topics_xpath = config.get("topics_xpath", "")
        self.is_premium_xpath = config.get("is_premium_xpath")

        # Crawl mode
        allow_recursion = True
        if start_urls:
            # To scrape a pool of urls without adding any more
            self.start_urls = start_urls
            allow_recursion = False
            self.parse_start_url = self.parse_item
        elif mode == "LATEST":
            self.start_urls = [config["start_latest"]]
            follow = False
        elif mode == "ALL":
            self.start_urls = [config["start_all"]]
            follow = True
        else:
            raise Exception(f"Unavailable mode selected. mode={mode} doesn't exist.")


        # Create rules
        self.rules = {
            # 
            # Match only articles (format: domain/topic/topic/YYYY/MM/DD/xxxxx.html)
            Rule(
                LinkExtractor(
                    # final_re = domain + re (without the domain a lot of newspapers can fail)
                    allow=[self.allowed_domains[0] + re_str for re_str in self.re_article_list], 
                    allow_domains=self.allowed_domains, 
                    unique=True
                ), 
                callback='parse_item', 
                follow=follow
            ),
            # Match any other page (without /YYYY/MM/DD which is unique for articles)
            Rule(
                LinkExtractor(
                    allow=[self.allowed_domains[0] + re_str for re_str in self.re_else_list], 
                    allow_domains=self.allowed_domains, 
                    unique=False
                ), 
                follow=follow
            ),
        } if allow_recursion else {}
        
        # ===== AMP Middleware conf =====
        # This setting must contains old_str and new_str:
        #       - old_str: Substring of the path which is going to be replaced
        #       - new_str: New substring to reload the webpage with the amp version
        self.amp_redirect = config.get("amp_redirect", {}) 

        # Rules will be compiled here
        super().__init__(self.name, **kwargs)


    def parse_item(self, response):
        news_item = NewsItem()
        news_item["html"] = response.body
        news_item["url"] = response.request.url
        news_item["is_premium"] = True if self.is_premium_xpath and response.xpath(self.is_premium_xpath) else False
        news_item["topic_list"] = self.extract_topics(response) if self.topics_xpath else []

        # In case the newspaper contains (sometimes) a info json (scheme.org)
        if self.info_xpath:
            json_str = response.xpath(self.info_xpath).getall()
            if json_str:
                extract_schemeorg(json_str, news_item, response, self)  
        yield news_item


    def extract_topics(self, response):
        """ Extract any topic
        """
        return list(filter(
            None,
            [topic.strip().title() for topic in response.xpath(self.topics_xpath).getall()]
        ))
