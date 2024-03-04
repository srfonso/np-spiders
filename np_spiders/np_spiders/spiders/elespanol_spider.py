from np_spiders.spiders.general import GeneralSpider

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class ElEspanolSpider(GeneralSpider):
    name = "elespanol_spider"

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/[\w\-/]*_\d+\.html"] # Any article -> ends with _123.html
    re_else_list = [r'/(?!\S*_\d+\.html)[\D/]+'] # any category web page, without "_123.html"