from np_spiders.spiders.general import GeneralSpider

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class LaVanguardiaSpider(GeneralSpider):
    name = "lavanguardia_spider"

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/(?!\S*/pdf.html)[\w\-/]+/\d+/\d+/.*\.html"] # Any article -> ends with /XXXX/YYYYY/....html
    re_else_list = [r'/(?!\S*\.html)[\w\-/]+'] # any category web page, without ".html"