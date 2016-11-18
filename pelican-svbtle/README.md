# Pelican-svbtle

This theme is a copy of a copy and is based on [Svbtle.com](http://www.svbtle.com).

Originally ported to [Pelican](http://pelican.notmyidea.org) by [William Ting](https://github.com/wting/) - download the [repository](https://github.com/wting/pelican-svbtle) or read the original [README file](https://github.com/wting/pelican-svbtle#readme).

Then [responsive adaptations](https://github.com/CNBorn/pelican-svbtle/tree/responsive) were made by [Tyler Xing(me)](https://github.com/CNBorn).

Reorganized by [James Cooke](https://github.com/jamescooke).

This is a adaptation specified for [Tyler Xing's Blog](http://cnborn.net).

### FROM OFFICIAL REPO

Please refer to Pelican theme [install instructions](http://pelican.notmyidea.org/en/latest/pelican-themes.html).

## SETTINGS.PY

These are the Pelican global variables currently supported by the theme:

- `GOOGLE_ANALYTICS`
- `DISQUS_SITENAME`
- `LINKS(('name1', 'url1'), ('name2', 'url2'))`
- `DEFAULT_DATE_FORMAT = ('%b %d, %Y')`: suggested date format
- `FEED_DOMAIN = SITEURL`

## MODIFICATION

- Accent color can be changed by editing `@accent` in `./static/css/style.less`.

- A different Pygmentize theme can be used by editing `./Makefile` and running `make pygments`.

## AUTHORS

William Ting, Tyler Xing, James Cooke

## LICENSE

Released under MIT License, full details in `LICENSE` file.
