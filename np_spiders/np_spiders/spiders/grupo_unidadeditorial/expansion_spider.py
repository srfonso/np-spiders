from np_spiders.spiders.general import GeneralSpider
from np_spiders.settings import DOWNLOADER_MIDDLEWARES

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class ExpansionSpider(GeneralSpider):
    name = "expansion_spider"
    
    # Custom settings (settings can't be updated dynamically f.e inside __init__)
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': dict(
            {"np_spiders.middlewares.PaywallAMPMiddleware":500}, # Custom new middleware
            **DOWNLOADER_MIDDLEWARES # Append general settings middleware
        )
    }