from np_spiders.spiders.general import GeneralSpider

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class PSOESpider(GeneralSpider):
    name = "psoe_spider"

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/actualidad/noticias-actualidad/[^?]+"] # Any article
    re_else_list = [r"/actualidad/noticias-actualidad/(?![\w\-\d]+).*"] # any other page