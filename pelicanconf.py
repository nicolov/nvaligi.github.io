#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Nicolò Valigi'
SITENAME = u'Nicolò Valigi | personal site'
SITEURL = 'http://nicolovaligi.com'

PATH = 'content'

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

LINKS = []
SOCIAL = []

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

STATIC_PATHS = ['images', 'pdfs']
ARTICLE_EXCLUDES = ['ignore']

THEME = '/Users/niko/blog/pelican-svbhack'

SUMMARY_MAX_LENGTH = 30

# svbhack
USER_LOGO_URL = '/images/logo_white.jpg'
TAGLINE = """Chronicles of (constant) learning."""