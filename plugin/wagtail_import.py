from collections import defaultdict
import datetime
import logging

from pelican import signals

from operator import attrgetter, itemgetter
from functools import partial

from pelican.generators import ArticlesGenerator, Generator
from pelican.contents import Article, Page, Static
from pelican.utils import copy, mkdir_p
from pelican.readers import BaseReader, Readers

from wagtail_client import WagtailClient

from dateutil import parser


logger = logging.getLogger()


class WagtailGenerator(ArticlesGenerator):
    def __init__(self, *args, **kwargs):
        """initialize properties"""
        self.articles = []  # only articles in default language
        self.dates = {}
        self.categories = defaultdict(list)
        self.authors = defaultdict(list)
        super(WagtailGenerator, self).__init__(*args, **kwargs)

        # 'cause settings is initialized in super
        # self.client = ButterCMS(self.settings.get('BUTTER_CONFIG')['api_key'])
        self.client = WagtailClient(self.settings.get('WAGTAIL_BASE_URL'))

    # Private helper function to generate
    def _generate_articles(self):
        DEFAULT_CATEGORY = self.settings.get('DEFAULT_CATEGORY')
        baseReader = BaseReader(self.settings)

        posts = []
        total_count = 0
        page = 1
        while True:
            # Paginate through all pages
            result = self.client.get({'limit': 3, 'offset': page - 1, 'type': "blog.BlogPage"})
            if 'items' in result:
                posts.extend(result['items'])

            if result['meta']['has_next']:
                page += 1
            else:
                break
        all_articles = []
        counter = 0
        for post in posts:
            counter += 1
            logger.info('GET TO article: %s' % post['title'])
            logger.info('counter: %s' % str(counter))
            date = parser.parse(post['meta']['first_published_at'])
            title = post['title']
            content = post['body']
            author = "Makoto Mochizuki"# post['authors'] # 空なのでとりあえず
            authorObject = baseReader.process_metadata('author', author)
            slug = post['meta'].get('slug', None)
            logger.info('--HAS slug: %s' % str(slug))
            categoryObj = None
            category = DEFAULT_CATEGORY
            categoryObj = baseReader.process_metadata('category', category)

            metadata = {'title': title,
                        'date': date,
                        'category': categoryObj,
                        'authors': [authorObject]}
            if slug:
                metadata['slug'] = slug


            article = Article(content=content,
                                metadata=metadata,
                                settings=self.settings,
                                context=self.context,
                                override_save_as=True)

            # # This seems like it cannot happen... but it does without fail.
            article.author = article.authors[0]
            all_articles.append(article)

        return all_articles

    def generate_context(self):
        # Update the context (only articles in default language)
        self.articles = self.context['articles']

        all_articles = []

        new_articles = self._generate_articles()
        all_articles.extend(new_articles)

        self.articles.extend(all_articles)

        for article in self.articles:
            # only main articles are listed in categories and tags
            self.categories[article.category].append(article)
            if hasattr(article, 'tags'):
                for tag in article.tags:
                    self.tags[tag].append(article)
            for author in getattr(article, 'authors', []):
                self.authors[author].append(article)

        # This may not technically be right, but...
        # Sort the articles by date too.
        self.articles = list(self.articles)
        self.dates = self.articles
        self.dates.sort(key=attrgetter('date'),
                        reverse=self.context['NEWEST_FIRST_ARCHIVES'])

        # and generate the output :)

        # order the categories per name
        self.categories = list(self.categories.items())
        self.categories.sort(reverse=self.settings['REVERSE_CATEGORY_ORDER'])

        self.authors = list(self.authors.items())
        self.authors.sort()

        logger.info('++++++++++++++++++++++++++++++++++++')
        logger.info('GOT categories %s' % str(self.categories))
        logger.info('++++++++++++++++++++++++++++++++++++')

        self._update_context(('articles', 'dates', 'categories', 'authors'))
        # self._update_context(('articles', 'dates'))
        # Disabled for 3.3 compatibility for now, great.
        # self.save_cache()
        # self.readers.save_cache()

        # And finish.
        signals.article_generator_finalized.send(self)

    # def generate_output(self, writer):
    #     # Intentionally leave this blank
    #     pass

    def generate_pages(self, writer):
        """Generate the pages on the disk"""
        write = partial(writer.write_file,
                        relative_urls=self.settings['RELATIVE_URLS'],
                        override_output=True)

        # to minimize the number of relative path stuff modification
        # in writer, articles pass first
        self.generate_articles(write)


def get_generators(pelican_object):
    return WagtailGenerator


def register():
    signals.get_generators.connect(get_generators)
