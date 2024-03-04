# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from newspaper import Article, Config, build, ArticleException
from langdetect import detect, LangDetectException
from np_spiders.utils import parse_datetime

class NewspaperParser:
    def process_item(self, item, spider):
        """ Process item to extract article info using newspaper3k to autocomplete
        those items with missing data.

        item["url"] and item["html"] must be filled from the spider.
        """

        # Fields which are going to be extracted from Article()
        fields = [
            "title",
            "text",
            "summary",
            "keywords",
            "movies",
            "top_image",
            "authors",
            "publish_date"
        ]
        
        try:
            # Parse the downloaded article webpage using newspaper3k lib
            art = Article(url=item["url"])
            art.download(input_html=item["html"])
            art.parse()
            art.nlp()
            
            # Fill all parsed data that has not been extracted yet
            [self._process_field(item, art, field) for field in fields]
            if not item.get("lang", None):
                item["lang"] = self.detect_lang(art.text)
            item["available"] = True

        except ArticleException as e:
            spider.logger.error(
                "(" + e.__class__.__name__ + ")"
                + f"({spider.name})"
                + "(Newspaper3k article info extraction error)" 
                + f"({item['url']})"
            )
            item["available"] = False

        # Once the html has been parsed, it will be deleted.
        item.pop('html', None)

        # Parse date (to make sure it is aware in case of being naive)
        date_aware = parse_datetime(item["publish_date"], spider.logger)
        # Re parsed to string to save it
        item["publish_date"] = date_aware.strftime('%Y-%m-%dT%H:%M:%S%z') if date_aware else None

        # Detect articles with less than 500 and throw a warning (it could be a 
        # parse error) 
        if len(item["text"]) < 500:
            spider.logger.warning(
                f"({spider.name})"
                + "(Article with less than 500 characters)" 
                + f"({item['url']})"
            )

        return item


    def _process_field(self, item, article, field):
        """ Extract information for an especific field using NewsPaper3k library
        in case it has not been extracted yet
        """
        if (field not in item) or (not item[field]):
            item[field] = getattr(article, field)



    def detect_lang(self, text):
        """Detect language of a text and return its language ISO 639-1 code

        Parameters
        ----------
        text: string
            Target text to detect its language.

        max_length: int
            Int > 0. LanguageDetect lib return ISO 639-1 codes, but some of them
            (zh-cn, zh-tw) have more caracters than the accepted from LanguageField
            (max 3). This param is used to control the returned length.

        Returns
        -------
        lang: string
            Language ISO 639-1 codes or "" in case of error.
        """
        try:
            # f.e 'zh-cn' -> 'zh-' (3 is the max of LanguageField)
            # clean in case of 'zh-' -> 'zh'
            lang = detect(text).split("-")[0]

        except LangDetectException as e:
            #logger.warning(
            #    "(" + e.__class__.__name__ + ")"
            #    '(Unable to detect language from "' + str(text) + '")'
            #)
            lang = ""

        return lang