from np_spiders.spiders.general import GeneralSpider
from np_spiders.settings import DOWNLOADER_MIDDLEWARES

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class ABCESSpider(GeneralSpider):
    name = "abc_es_spider"

    # Custom settings (settings can't be updated dynamically f.e inside __init__)
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': dict(
            {"np_spiders.middlewares.PaywallAMPMiddleware":500}, # Custom new middleware
            **DOWNLOADER_MIDDLEWARES # Append general settings middleware
        )
    }

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/[\w\-/]+\-nt\.html"]
    re_else_list = [r'/(?!\S*\-nt\.html)[\D/]+'] # any category web page, without numbers and without -nt.html