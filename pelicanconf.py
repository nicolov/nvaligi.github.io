#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os

AUTHOR = "Nicolò Valigi"
SITENAME = "Nicolò Valigi"
SITEURL = "https://nicolovaligi.com"

TIMEZONE = "Europe/Rome"

DEFAULT_LANG = "en"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
AUTHOR_SAVE_AS = ""
CATEGORY_SAVE_AS = ""

# Blogroll

DISPLAY_PAGES_ON_MENU = False

MENUITEMS = (
    ("Talks", "/pages/talks.html"),
    ("Robotics for developers", "/pages/robotics-for-developers-tutorial.html"),
    ("Research", "/pages/research.html"),
)

LINKS = []
SOCIAL = []

DEFAULT_PAGINATION = 11

# This will get over-written by publishconf.py
RELATIVE_URLS = True

MD_EXTENSIONS = ["codehilite(css_class=highlight)", "extra"]

PATH = "content"
STATIC_PATHS = ["blog", "pages", "robotics-for-developers", "extra/CNAME"]
ARTICLE_PATHS = ["blog", "robotics-for-developers"]
ARTICLE_EXCLUDES = ["blog/ignore"]
PAGE_PATHS = ["pages"]
EXTRA_PATH_METADATA = {"extra/CNAME": {"path": "CNAME"}}

current_folder = os.path.dirname(os.path.abspath(__file__))
THEME = os.path.join(current_folder, "pelican-svbhack")

PUBLICATIONS_SRC = "content/bib.bib"

SUMMARY_MAX_LENGTH = 30

PLUGIN_PATHS = ["./pelican-plugins"]
PLUGINS = ["render_math", "pdf-img", "pelican-cite", "pelican-ipynb.markup"]

# svbhack
USER_LOGO_URL = "/blog/images/logo_white.jpg"
TAGLINE = """Writing about Software, Robots, and Machine Learning."""

# Get ipython notebooks summary from the meta file
IPYNB_USE_META_SUMMARY = True
