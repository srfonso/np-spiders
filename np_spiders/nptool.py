import os
import json
import time
import logging
import argparse
import inspect
import pkgutil
import importlib
import tldextract
from pathlib import Path
from collections import defaultdict
from np_spiders.settings import CONF_JSON_PATH
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

logger = logging

BASE_DUMP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dumps")

def _configure_argparse():
    """Configuration of the parser."""

    parser = argparse.ArgumentParser(
        description='Use the Newspaper scraper tool.',
    )

    # Global config (proxy, number of threads, input, output f.e)
    parser.add_argument(
        '-L', '--loglevel', 
        dest='loglevel',
        metavar='LEVEL', 
        default="WARNING",
        help=f"log level (default: WARNING). Options: {list(logging._nameToLevel.keys())}",
        type=_valid_loglevel
    )

    parser.add_argument(
        '-f', '--foldername',
        dest="foldername",
        metavar='FOLDERNAME', 
        type=str, 
        required=True,
        help='Result foldername where all the articles from each domain will be stored (in different files).',
    )

    parser.add_argument(
        '-g', '--generaliser',
        dest="generaliser",
        action='store_true',  # Automatically stores True if `-g` or `--generaliser` is specified, otherwise False
        default=False,  # This is actually redundant for `store_true` action, as it defaults to False
        help=('Enable or disable the generaliser feature. This will active the general crawler and'
        ' any url will be scraped (allowing information extraction from any website but with'
        ' worse results). Default is False.'),
    )
    
    optional_exclusive_group = parser.add_argument_group('Source formats to scrape (required)')
    group = optional_exclusive_group.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-u', '--url',
        dest="url",
        metavar="URL",
        type=str, 
        help='url target element to scrape.',
    )
    group.add_argument(
        '-urls', '--urlsfile',
        dest="urlsfile",
        metavar='FILE', 
        type=str, 
        help='target file with urls to scrape.',
    )

    # Once parser has been configured, arguments will be parsed
    args = parser.parse_args()
    return args


def _valid_loglevel(loglevel):
    if loglevel not in logging._nameToLevel.keys():
         raise argparse.ArgumentTypeError(
            "Not a valid level for loggings: {0!r}".format(loglevel)
        )
    return loglevel


def _setup_logging():
    #logging.setLoggerClass(Logger) # Personalized Logger class
    global logger
    logger = logging.getLogger(__name__)


def _configure_logging(loglevel):
    rootLogger = logging.getLogger()

    # Set level
    if loglevel:
        level = logging.getLevelName(loglevel)
        rootLogger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter('{asctime}.{msecs:03.0f}|{levelname}|{name}|{message}', datefmt = '%Y-%m-%d %H:%M:%S', style = '{')

    # Add stream handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    rootLogger.addHandler(handler)


def _import_spiders(rute="np_spiders/spiders"):
    """ Imports automatically any spiders (or clases) from the rute.
        - pkgutil.iter_modules works with '/' : directory/to/path/module
        - importlib.import_module works with '.': directory.to.path.module
    """
    sp_classes = []
    for finder, name, ispkg in pkgutil.iter_modules([rute]):
        if ispkg:
            sp_classes.extend(_import_spiders(rute + '/' + name))
        else:
            modulo = importlib.import_module(rute.replace('/', '.') + '.' + name)
            for member_name, member_value in inspect.getmembers(modulo):
                if inspect.isclass(member_value) and member_value.__module__ == modulo.__name__:
                    sp_classes.append(member_value)
    return sp_classes


def run_spiders(urls_by_domain, folderpath, loglevel, use_general=False):
    """ Lunch an spider for each group of urls

    Parameters
    ----------
    urls_by_domain: dict
        Dict with each domain as keys and their urls as value.

    folderpath: class (PosixPath)
        PosixPath from pathlib.Path class with the foldername where each item 
        will be stored.
    """

    # Read configuration for this spider
    if not use_general:
        with open(CONF_JSON_PATH,'r') as file:
            conf_dict = json.load(file)
            available_scrapers = {
                sp_config["allowed_domains"][0]: sp_name 
                for sp_name, sp_config  in conf_dict.items()
            }

    # Override settings
    settings = get_project_settings()

    process = CrawlerProcess(settings, install_root_handler=False)
    
    # Forcing scrapy loggers to follow the root loglevel (scrapy bug?)
    scrapy_loggers = ['scrapy', 'scrapy.core.engine', 'scrapy.extensions', 'scrapy.spiders', 'scrapy.middleware', 'charset_normalizer']
    for logger_name in scrapy_loggers:
        logging.getLogger(logger_name).setLevel(loglevel)    
    
    for domain, urls in urls_by_domain.items():
        # Save each domain in a different file in the foldername 
        # (Scrapy can't handle multiple writings in the same file)
        settings.update({
            'FEEDS': {
                f'{(BASE_DUMP_PATH / folderpath / domain.lower().replace(".","_")).as_posix()}.json': {
                    'format': 'json',
                },
            },
        })
        sp_name = available_scrapers.get(domain, None) if not use_general else "general"
        if sp_name:
            # Add a new spider to the process to extract the given urls
            process.crawl(sp_name, start_urls=urls)
        else:
            logger.warning(f"{len(urls)} urls from {domain} not available to scrape.")
    process.start()


def group_by_domain(urls):
    """ Create a dict grouping each url with its domain.
    """
    urls_by_domain = defaultdict(list)
    
    for url in urls:
        extract_result = tldextract.extract(url)
        domain = "{}.{}".format(extract_result.domain, extract_result.suffix)
        urls_by_domain[domain].append(url)
    
    return dict(urls_by_domain)



def main():

    _setup_logging()
    args = _configure_argparse()
    _configure_logging(args.loglevel)

    # Create destination folder
    folderpath = Path(args.foldername)
    folderpath.mkdir(parents=True, exist_ok=True)

    # Get the urls_by_domain
    urls_by_domain = []
    if not args.url:
        try:
            with open(args.urlsfile, 'r') as file:
                urls = [line.strip() for line in file]
                urls_by_domain = (
                    group_by_domain(urls)
                    if not args.generaliser else 
                    {"general": urls}
                )
        except FileNotFoundError:
            logger.warning(f"File {args.urlsfile} not found.")
            return
    else:
        urls_by_domain = group_by_domain([args.url]) if not args.generaliser else {"general": [args.url]}

    start_time = time.time() # Tiempo inicial
    run_spiders(urls_by_domain, folderpath, args.loglevel, args.generaliser)
    end_time = time.time() # Tiempo final
    logger.info(f"Execution time: {(end_time - start_time):.3f} secs")


if __name__ == '__main__':
    main()