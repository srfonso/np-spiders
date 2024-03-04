from np_spiders.spiders.general import GeneralSpider

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class AsSpider(GeneralSpider):
    name = "as_spider"

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/[\w\-/]+\-n/"]
    re_else_list = [r'/(?!\S*\-n/)[\w\-/]+'] # any category web page (without -n/)
