from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    title = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = _("categories")
        ordering = 'title',

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = 'name',

    def __str__(self):
        return self.name


class Item(models.Model):
    """
    A representation of an RSS feed
    """
    date_published = models.DateTimeField()  # type: datetime
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(_("URL"), blank=True)
    guid = models.CharField(_("GUID"), max_length=255, unique=True, null=True, blank=True)
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL)
    categories = models.ManyToManyField(Category, related_name="items")

    class Meta:
        ordering = 'date_published',

    def __str__(self):
        date_fmt = self.date_published.strftime("%Y-%m-%d %H:%M:%S")
        return f'{self.title} [{date_fmt}]'
