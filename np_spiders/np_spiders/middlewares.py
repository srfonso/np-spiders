# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from .settings import USERAGENTS
from w3lib.http import basic_auth_header
import random


class PaywallAMPMiddleware(object):
    """ Middleware responsible for detect Premium articles with paywall and by pass 
    them by redirecting the page to the amp version (which includes all info inside 
    the body) 
    """

    def process_response(self, request, response, spider):
        # ByPass Paywall (a premium site which is not already an amp.domain. site)
        if (spider.amp_redirect["new_str"] not in request.url 
                and response.xpath(spider.is_premium_xpath).get()):
            bypass_url = response.xpath("//link[@rel='amphtml']/@href").get()
            if not bypass_url:
                bypass_url = request.url.replace(
                    spider.amp_redirect["old_str"],
                    spider.amp_redirect["new_str"]
                )
            # Prevents Scrapy from considering this link as duplicate (dont_filter=True)
            bypass_request = request.replace(url=bypass_url, dont_filter=True)
            return bypass_request

        return response


class RotateUserAgentMiddleware:

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        useragent = random.choice(USERAGENTS)
        request.headers['User-Agent'] = useragent
        # Add custom headers to the request
        if spider.custom_headers:
            request.headers.update(spider.custom_headers)
        spider.logger.info(f"(USER-AGENT)({useragent})")


class WebshareMiddleware(object):
    """ Webshare.io proxy service middleware.

    Author: https://github.com/soubenz/Webshare-Scrapy
    """
    url = "http://p.webshare.io:80"
    download_timeout = 180
    countries = ['RU', 'US', 'UA', 'NL', 'FR', 'DE', 'PL', 'GB', 'CN', 'CZ',
                       'EE', 'LV', 'ES', 'JP', 'TR', 'PT', 'AM', 'IR', 'EG',
                       'PK', 'MD', 'IT', 'BD', 'FI', 'GR', 'SE', 'GE', 'KZ',
                       'VN', 'ZA', 'BG', 'NG', 'QA', 'HK', 'IS', 'ID', 'KR',
                       'MA', 'SA', 'BY', 'UZ', 'TH', 'CY', 'SG', 'IN', 'IL',
                       'DE', 'UA', 'IN', 'AL']
    _settings = [
        ('country', str),
        ('user', str),
        ('password', str),
        ('download_timeout', int),
    ]

    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)
        crawler.signals.connect(o.open_spider, signals.spider_opened)
        return o

    def open_spider(self, spider):
        self.enabled = self.is_enabled(spider)
        if not self.enabled:
            return

        for k, type_ in self._settings:
            setattr(self, k, self._get_setting_value(spider, k, type_))
        spider.logger.info("Using Webshare")

        self._proxy_auth = self._create_proxy_auth()
        spider.logger.info("Using webshare at %s (apikey: %s)" % (
            self.user,
            self.password)
        )

    def is_enabled(self, spider):
        return (
            getattr(spider, 'webshare_enabled', False) or
            self.crawler.settings.getbool("WEBSHARE_ENABLED")
        )

    def _get_setting_value(self, spider, k, type_):
        o = getattr(self, k, None)
        s = self._settings_get(
            type_, 'WEBSHARE_' + k.upper(), o)
        return getattr(
            spider, 'webshare_' + k,  s)

    def _settings_get(self, type_, *a, **kw):
        if type_ is int:
            return self.crawler.settings.getint(*a, **kw)
        elif type_ is bool:
            return self.crawler.settings.getbool(*a, **kw)
        elif type_ is list:
            return self.crawler.settings.getlist(*a, **kw)
        elif type_ is dict:
            return self.crawler.settings.getdict(*a, **kw)
        else:
            return self.crawler.settings.get(*a, **kw)

    def process_request(self, request, spider):
        if self._is_enabled_for_request(request):
            request.meta['proxy'] = self.url
            request.meta['download_timeout'] = self.download_timeout
            request.headers['Proxy-Authorization'] = self._proxy_auth
            self.crawler.stats.inc_value('webshare/request_count')
            self.crawler.stats.inc_value('webshare/request/method/%s' %
                                         request.method)

    def _is_enabled_for_request(self, request):
        return self.enabled

    def _create_proxy_auth(self):
        if self.user and self.password:
            if self.country in self.countries:
                user_rotate = '{}-{}-rotate'.format(self.user, self.country)
                return basic_auth_header(user_rotate, self.password)
            else:
                user_rotate = '{}-rotate'.format(self.user)
                return basic_auth_header(user_rotate, self.password)