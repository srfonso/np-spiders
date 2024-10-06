import re
import json
import dateutil.parser
import pytz

def parse_datetime(date, logger, tz=pytz.timezone("Europe/Madrid")):
    """ If date is a string, parse it to datetime 
    Also make it ware (in case of being naive)

    Parameters
    ----------
    date: string | datetime
        Datime to check if it is aware or string to parse. 
    tz: datetime.tzinfo
        Timezone of the date.
    """
    try:
        # Parse date in case of being a string
        if isinstance(date, str):
            date = dateutil.parser.parse(date)
        # Make aware
        if not date.tzinfo:
            date = date.astimezone(tz)
        return date
    except Exception as e:
        logger.error("(" + e.__class__.__name__ + ")(" + str(e) + ")")
        return None


def extract_schemeorg(json_list_str, news_item, response, spider):
    """ Extract information from a json whose data follows schema.org

    This function receive all the schemes from a webpage and it's able to extract
    the Article scheme information (https://schema.org/Article) from different 
    input formats. f.e:
        - Receiving a list of strings, choose the Article str before loading the json
        - Receiving a unique string whcih contains a list of schemes and,
         after loading its content to json, extract the dict related to Article

    NOTE: https://schema.org/Recipe elements won't be extracted. 

    TODO: Accept other type of items, https://schema.org/MediaObject ??? 

    Parameters
    ----------
    json_list_str: list
        List of strings which contains a scheme.org json. 

    news_item: string
        Target item where all information is going to be inserted.

    response: callable
        The scrapy.Response object with the Newspaper article.

    spider: callable
        The scrapy.Spider which scraped the article.

    """
    # From a list of scheme.org strings elements choose that one which contains "Article"
    # (In that case, @type tag contains Article)
    json_str = [aux_str for aux_str in json_list_str if "Article" in aux_str]
    json_str = json_str[0] if json_str else ""
    try:
        info_json = json.loads(json_str, strict=False)

        # Some times webpages contains the json info inside a '[]' and sometimes not
        # Also, sometimes inside the list we have all the schemes.org elements from
        # the webpage, that's Article scheme, Website scheme, etc..
        if type(info_json) is list:
            # Extract only the Article element
            # https://schema.org/Article
            info_json = [dict_elem for dict_elem in info_json if "Article" in dict_elem["@type"]][0]

        # Fill all available information
        aux_url = info_json.get("mainEntityOfPage", {})
        news_item["url"] = aux_url if type(aux_url) is str else aux_url.get("@id", response.request.url)
        news_item["title"] = info_json.get("headline", None)
        news_item["text"] = info_json.get("articleBody", None)
        news_item["lang"] = _lang_to_iso(info_json.get("inLanguage", None))
        news_item["contentLocation"] = _extract_property(info_json, "contentLocation")
        news_item["authors"] = _extract_property(info_json, "author")
        news_item["publish_date"] = info_json.get("dateModified", None)

    except (json.JSONDecodeError) as e:
        spider.logger.error(
            "(" + e.__class__.__name__ + ")"
            + f"({spider.name})"
            + "(Unable to extract json info from article)" 
            + f"({response.request.url})"
        )

def _lang_to_iso(lang):
    """ RFC-5646 languages codes to ISO 639-1
    """
    # Split the RFC 5646 tag by '-' and take the first part
    if lang:
        lang = lang.split('-')[0]
    return lang


def _extract_property(schema_data, property):
    """ Extract property data from scheme.org structure with the following formats:
        - a) "prop" : "text"
        - b) "prop" : {"@type": ..., "name": "text"}
        - c) "prop" : [{"@type": ..., "name": "text"}, ...]
    
    Parameters
    ----------
    schema_data: dict

    property: str

    Return
    ----------
    ret: list
    """

    prop_data = schema_data.get(property, [])
    # a) text
    if isinstance(prop_data, str):
        return _parse_content(prop_data)
    
    # b) or c)
    result = []
    prop_data = prop_data if isinstance(prop_data, list) else [prop_data]
    for elem in prop_data:
        elem = elem.get("name", "")
        # In case the name is stored in a list of variations "name": [Pepe Perez, Jose Perez]
        if isinstance(elem, list):
            if elem:
                elem = elem[0]
            else:
                elem = ""
        result += _parse_content(elem)

    return result


def _parse_content(content):
    """ Sometimes Newspapers includes more info inside a text, using separators 
    such as '/' or ','.. f.e: ElPais.com often uses this -> 'name': 'Pepe / Ramon'

    Separators: ,|/;-

    Parameters
    ----------
    content: str

    Return
    ----------
    ret: list
    """
    return [c.strip().title() for c in re.split('[,|:/;\-]', content)]