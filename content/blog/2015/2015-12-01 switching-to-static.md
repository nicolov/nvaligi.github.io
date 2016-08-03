Title: Building static sites with Django
Date: 2015-12-01
Category: web, backend, django
Slug: switch-static-site-for-side-projects
Summary: How a few lines can transform a Django web-app into a static site that's fast and easy to host.

Using Django to build lighting fast static sites that are easy to deploy.

Technology choices have a way of staying with you when keeping side projects alive for more than a few years. In my case, Django has been great in the development and iteration phases, but deployment has given me more headaches that I would hope for.

In this post, I'm going to talk about my experience generating, serving and maintaining a faster and more reliable site using a static generator for Django.

## The project

I co-run a marketing site that does around 10k daily hits, with around 100 content-heavy pages available in 10 languages around the world. Ideally, I would want to run this from a single small VPS (1GB ram) without UptimeRobot alerts setting off in the middle of the night.

While undeniably solid, I felt that the `uwsgi` + `nginx` stack needed a bit more loving care that I had to give. All things considered, I'd rather be programming rather than writing configuration files or reading logs.

At the same time, it looks like static site generators are everyone's new favourite open source project (after JS frameworks, of course). I've had good luck with [Pelican](https://github.com/getpelican/pelican) in the past, but prefer to keep the content in the database, not in a tree of text files.

That's why I've decided to build a static site alongside Django, keeping the lovely admin interface and saving a lot of work in the process.

## Creating a static site with Django

Luckily, the [django-medusa](https://github.com/mtigas/django-medusa) app met most of my requirements:

- *minimal* code changes are required on Django's side: the same project can be run under `uwsgi` or generated as a static tree;
- does its magic by hacking Django's testing machinery, so it doesn't have external dependencies and doesn't need to fire up a web server;
- did I mention I got to reuse dozens of templates, template tags, and database queries?

### Implementation details

I needed to make sure all arguments were passed in as part of the URL (and not as query parameters). This required a bit of regex magic on the URL definitions. For example, I wanted to have optional trailing fragments with the current page and had to use the horrible:

```
(r'^cool-page(?:/(?P<page>[0-9]+))?/$')
```

to make sure that the URLs would be reversed correctly (forgetting the final slash is severely punished by the SEO gods).

The biggest chore is defining a list of all URLs that should be hit while rendering the site. On the bright side, I consider this a kind of *integration testing* of the database, views, and template layers.

Most URL definitions will use `django.core.urlresolvers.reverse_lazy` to refer to names paths in the `urls.py` module. For example:

```
class FixedPages(DiskStaticSiteRenderer):

	def get_paths(self):
		return set([
			reverse_lazy('index'),
			reverse_lazy('about-page'),
			reverse_lazy('top-10')
		])

```

Paginated lists that hit the database are trickier, since the total number of pages is not known in advance, and an additional database query is needed.

```
def get_paths(slug):
	qs = Article.objects.filter(category__slug=slug)
	pages_range = range(2, (qs.count()-1) // 10 + 2)

	return set([
		[rev('category_list', args=(slug, page)) for page in pages_range] +
		[rev('category_list', args=(slug,))]])
```

I've done some more hacking to render multiple domains and store the HTMLs in different folders:

```
from django_medusa.renderers import DiskStaticSiteRenderer

def CustomHostDiskRenderer(DiskStaticSiteRenderer):

	def __init__(self, host_name):
		super(DiskStaticSiteRenderer, self).__init__(self)

		self.http_host = host_name
		self.DEPLOY_DIR = os.path.join(
			settings.MEDUSA_DEPLOY_DIR,
			self.http_host)
```

## A good choice

It now takes around 1 minute to completely rebuild my static site in a few (human) languages, and I've yet to feel the need to set up incremental builds to speed up the process. A few lines in nginx's configuration got me:

- crazy speed that will hopefully be appreciated by users and rewarded by Google,

- built-in integration testing since all pages are generated for each deployment,

- freedom from cache invalidation and `uwsgi` configuration headaches, with plenty of free RAM.

While many bigger sites will opt for a static site to scale better under load, I've found these tricks to be useful for smaller side projects as well.
