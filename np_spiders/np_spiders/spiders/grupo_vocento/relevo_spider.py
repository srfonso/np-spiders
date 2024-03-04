from np_spiders.spiders.general import GeneralSpider
from np_spiders.settings import DOWNLOADER_MIDDLEWARES

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class RelevoSpider(GeneralSpider):
    name = "relevo_spider"

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/[\w\-/]+\-nt.html"]
    re_else_list = [r'/[\D/]+/$'] # any category web page, without numbers (/../../)