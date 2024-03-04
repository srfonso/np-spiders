from np_spiders.spiders.general import GeneralSpider

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class OkDiarioSpider(GeneralSpider):
    name = "okdiario_spider"

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/[\w\-/]*\-\d+"] # Any article -> ends with -XXXXXX
    re_else_list = [r'/(?!\S*\-\d+)[\w\-/]+/'] # any category web page, without -XXXXXX"