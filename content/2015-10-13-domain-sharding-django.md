Title: Domain sharding in Django
Date: 2015-10-13
Category: Web Backend Django
Slug: domain-sharding-django
Summary: Speed up serving of media files in Django by using CDNs with different domains

It's 2015. Static files should be served by a CDN. Period. This has several advantages, the most obvious being:

- it frees up the resources of your main server, both in bandwidth and CPU terms
- since requests to CDN assets are on a different domain, the browser doesn't have to send (useless) cookies with every request
- most CDN providers have datacenters all over the world to make your site *more faster* for more users.

In this article, we are going to look at **domain sharding**, an additional trick to speed up loading of media-heavy sites.

## Why more is more

Once upon a time, when broadband was far on the horizon, browsers used to have a tight ceiling on the maximum numbers of concurrent requests to a single domain (around 2). These days the situation has improved, and mainstream browsers have pushed this limit up to around 7-8. However, there's still room for improvement by letting browsers load assets from different domains, thus lifting the actual *global* connection limit and having your media downloads saturate the user's connection.

## Doing it in Django

While not part of the many batteries included with Django, sharding of media files is pretty easy to implement. There's actually a [project](https://github.com/coagulant/django-webperf) on Github with a nice implementations a a custom `Storage`. Unfortunately, I had some issues when using it other 3rd party modules. Anyhow, I'm posting a slightly revised version which is friendlier and uses inheritance on the `__init__` function.

<script src="https://gist.github.com/nicolov/7d993cc12203e7b81e08.js"></script>

As a side note, I'm also using the `easy_thumbnails` module for, you guessed it, thumbnails, and also had to set the `THUMBNAIL_DEFAULT_STORAGE` variable in `settings.py` to make sharding work for images.

## Mobile, be aware

Some recent articles suggest that excessive reliance on domain sharding may actually be detrimental for mobile users due to the behaviour of mobile networks. Have a look [here](http://www.mobify.com/blog/domain-sharding-bad-news-mobile-performance/) if your website has many visitors on 3/4G networks.