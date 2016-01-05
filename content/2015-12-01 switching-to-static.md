Title: Switch to a static site for your side projects
Date: 2015-12-01
Category: Backend Django
Slug: switch-static-site-for-side-projects
Summary: Static websites are becoming more and more widespread. While the scaling benefits are clear, let's look at how they can reduce the (mental) load when managing content-heavy sites.

Technology choices have a way of staying with you when keeping side projects alive for more than a few years. In my case, Django has been great in the development and iteration phases, but deployment has given me more headaches that I would hope for.

In this post, I'm going to talk about my experience generating, serving and maintaining a faster and more reliable site using a static generator for Django.

## The project

I co-run a marketing site that does around 10k daily hits, with around 100 content-heavy pages available in 10 languages around the world. Ideally, I would want to run this from a single small VPS (1GB ram) without UptimeRobot alerts setting off in the middle of the night.

While undeniably solid, I felt that the `uwsgi` + `nginx` stack needed a bit more loving care that I had to give. All things considered, I'd rather be programming rather than writing configuration files or reading logs.

At the same time, it looks like static site generators are everyone's new favourite open source project (after JS frameworks, of course). I've had good luck with [Pelican](https://github.com/getpelican/pelican) in the past, but prefer to keep the content in the database, not in a tree of text files.

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

Paginated lists that hit the database are trickier, since you don't know their total number in advance and need to create a `QuerySet` beforehand:

```
def get_category_paths(slug):
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

While many web developers are moving towards static*-er* sites to scale better, I've found that smaller websites will have a different set of benefits:

- higher reliability as the app server doesn't need to run on the production machine;
- no need to deal with complex cache mechanisms (that introduce even more deployment and maintenance complexities);
- automatic integration testing, since each URL is pre-rendered and all errors show up immediately
