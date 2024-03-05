# NP SPIDERS
## A generic newspaper scraper
`np_spiders` is a scraping project that aims to extract news from a wide range of media sources. To achieve this, two main libraries are utilized:
- `Scrapy`: A Python framework for scraping and crawling.
- `Newspaper3k`: A Python library for extracting and curating articles.

Thanks to these two libraries, the project is capable of extracting and curating any type of news from almost any media outlet. There are two types of available media sources:
- Specialized spiders: For this, it is necessary to fill out a configuration file `spiders_conf.json` with specific information about that media outlet and create a specific spider inheriting from `GeneralSpider`.
- Generic sources: The project attempts to extract the maximum amount of information possible (either by extracting any possible schema.org from the HTML or using `newspaper3k`).

## Spider Execution
All available spiders can be found by running the following command `scrapy list` within the scrapy project folder `cd ./np_spiders/`. Currently, the following specialized spiders exist:
- abc_es_spider
- as_spider
- elconfidencial_spider
- eldiario_spider
- elespanol_spider
- elmundo_spider
- elpais_spider
- expansion_spider
- general (*more details throughout the documentation)
- huffpost_spider
- kiosko_spider
- lavanguardia_spider
- libertaddigital_spider
- marca_spider
- okdiario_spider
- psoe_spider
- relevo_spider

To execute any of these spiders, simply use the following command:
```bash
scrapy crawl <spider_name> -L <LOGLEVEL> -o <filename.ext>:<ext> -s CLOSESPIDER_PAGECOUNT=100 (Optional)
```

Additionally, there is an optional argument `-a mode=<ALL | LATEST>` (ALL by default). In this case, it will choose one of the two available URLs in the configuration file of the different spiders.
- ALL: Points to the main page of the media outlet and will attempt to download the maximum number of news articles.
- LATEST: Points to the "latest news" section and will download only news from that section.

Regarding `-o <filename.ext>:<ext>`, the available extensions can be either CSV or JSON. For example, `-o pruebas.json:json`.

## NPTOOL tutorial

`python nptool.py --help`
```bash
usage: nptool.py [-h] [-L LEVEL] -f FOLDERNAME [-g] (-u URL | -urls FILE)

Use the Newspaper scraper tool.

optional arguments:
  -h, --help            show this help message and exit
  -L LEVEL, --loglevel LEVEL
                        log level (default: WARNING). Options: ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
  -f FOLDERNAME, --foldername FOLDERNAME
                        Result foldername where all the articles from each domain will be stored (in different files).
  -g, --generaliser     Enable or disable the generaliser feature. This will active the general crawler andany url will be scraped (allowing information
                        extraction from any website but with worse results). Default is False.

Source formats to scrape (required):
  -u URL, --url URL     url target element to scrape.
  -urls FILE, --urlsfile FILE
                        target file with urls to scrape.
```

`nptool` is an additional tool that enables downloading and creating datasets from any media outlet based on a list of URLs. It has two main functions:
- Without the `-g` flag: In this case, all URLs that do not correspond to the listed media outlets, i.e., those without a specialized spider, will be ignored. JSON files will be created for each of the media outlets where a URL was present, within the chosen folder specified by the `-f` parameter.
- With the `-g` flag: It allows extracting any type of news and storing it within the specified folder in a file named `general.json`. In this case, the generic spider `general` will be used, so the information extraction will not be as precise as in the previous case. However, it enables obtaining information from a greater number of digital newspapers.

## Development by

[Cybersecurity and Privacy Protection Research Group (GiCP)](https://gicp.es)
- Member of Consejo Superior de Investigaciones Científicas (CSIC)

