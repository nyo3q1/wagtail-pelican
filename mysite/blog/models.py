from django.db import models

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.search import index

from wagtail.api import APIField

from rest_framework.fields import DateField


class BlogPageAuthor(Orderable):
    page = models.ForeignKey('blog.BlogPage', on_delete=models.CASCADE, related_name='authors')
    name = models.CharField(max_length=255)

    api_fields = [
        APIField('name'),
    ]


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]


class BlogPage(Page):
    published_date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('published_date'),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
    ]

    # Export fields over the API
    api_fields = [
        APIField('published_date'),  # Date in ISO8601 format (the default)
        APIField('published_date_display', serializer=DateField(format='%A $d %B %Y', source='published_date')),  # A separate published_date_display field with a different format
        APIField('body'),
        APIField('authors'),  # This will nest the relevant BlogPageAuthor objects in the API response
    ]
