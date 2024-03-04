from np_spiders.spiders.general import GeneralSpider

# Poner limite de páginas
#scrapy crawl <spider> -s CLOSESPIDER_PAGECOUNT=100

class LibertadDigitalSpider(GeneralSpider):
    name = "libertaddigital_spider"

    #==== Regular expression path (without domain) ====
    re_article_list = [r"/[\w\-/]+/\d{4}-\d{2}-\d{2}/.+"] # Webapge with /YYYY-MM_DD/...
    re_else_list = [r'/(?!.*\/\d{4}-\d{2}-\d{2}\/).*'] # any category web page, without /YYYY-MM_DD/