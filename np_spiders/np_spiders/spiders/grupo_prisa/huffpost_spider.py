from np_spiders.spiders.general import GeneralSpider

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100


class HuffPostSpider(GeneralSpider):
    name = "huffpost_spider"

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/[\w\-/]+.*\.html", r'/\d+/\d+/.+'] # huffpost and eltelevisero.huffingtonpost
    re_else_list = [r'/(?!\S*\.html)[\D/]+[\w\-]*'] # any category web page, without .html
