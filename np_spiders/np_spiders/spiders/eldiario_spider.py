from np_spiders.spiders.general import GeneralSpider

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class ElDiarioSpider(GeneralSpider):
    name = "eldiario_spider"

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/[\w\-/]*\d+\.html"] # Any article -> ends with XXXX.html
    re_else_list = [r'/(?!\S*\d+\.html)[\w\-/]+/'] # any category web page, without XXXX.html"