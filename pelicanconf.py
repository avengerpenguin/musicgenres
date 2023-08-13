import re

from voltaire.pelican import *


SITENAME = "Music Genres"
PATH = "./Music"
PAGE_PATHS = [""]
ARTICLE_PATHS = ["articles"]

PLUGINS += ['voltaire.search', 'yaml_metadata']
TEMPLATE_PAGES = {
    'search.html': 'search/index.html',
}

MENUITEMS_START = (
    ("Home", "/"),
    ("Search", "/search/"),
)

MARKDOWN["extension_configs"]["voltaire.graphviz"] = {}
TYPOGRIFY_IGNORE_TAGS = ['svg']