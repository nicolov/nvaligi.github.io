#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os

AUTHOR = u'Nicolò Valigi'
SITENAME = u'Nicolò Valigi'
SITEURL = 'http://nicolovaligi.com'

TIMEZONE = 'Europe/Rome'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll

'''
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)
'''

'''
MENUITEMS = (
    ('About', '/pages/about.html'),
    ('CV', '/pages/cv.html'),
)
'''

LINKS = []
SOCIAL = []

DEFAULT_PAGINATION = 10

# This will get over-written by publishconf.py
RELATIVE_URLS = True

MD_EXTENSIONS = ['extra']

PATH = 'content'
STATIC_PATHS = ['blog', 'robotics-for-developers', 'extra/CNAME']
ARTICLE_PATHS = ['blog', 'robotics-for-developers']
ARTICLE_EXCLUDES = ['blog/ignore']
PAGE_PATHS = ['pages']
EXTRA_PATH_METADATA = {
        'extra/CNAME': {'path': 'CNAME'},
}

current_folder = os.path.dirname(os.path.abspath(__file__))
THEME = os.path.join(current_folder, 'pelican-svbhack')

SUMMARY_MAX_LENGTH = 30

PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = ["render_math", "pdf-img"]

# svbhack
USER_LOGO_URL = '/blog/images/logo_white.jpg'
TAGLINE = """Chronicles of (constant) learning."""
