from voltaire.pelican import *

SITENAME = "History of Sound"
PATH = "./Music"
PAGE_PATHS = [""]
ARTICLE_PATHS = ["articles"]

PLUGINS += ["voltaire.search", "yaml_metadata"]
TEMPLATE_PAGES = {
    "search.html": "search/index.html",
}

INDEX_SAVE_AS = ""
ARCHIVES_SAVE_AS = AUTHORS_SAVE_AS = CATEGORIES_SAVE_AS = TAGS_SAVE_AS = ""

MENUITEMS_START = (
    ("Home", "/"),
    ("Search", "/search/"),
)

MARKDOWN["extension_configs"]["voltaire.graphviz"] = {}
TYPOGRIFY_IGNORE_TAGS = ["svg"]
