from django.db import models


class FakeModel(models.Model):
    required_field = models.CharField(max_length=1)
    blank_field = models.CharField(max_length=1, blank=True)
    null_field = models.CharField(max_length=1, null=True)
    default_field = models.CharField(max_length=1, default="Y")


class FakeModelWithM2M(models.Model):
    required_field = models.CharField(max_length=1)
    m2m_field = models.ManyToManyField("FakeRSSCategory")


class FakeRSSAuthor(models.Model):
    name = models.CharField(max_length=100)


class FakeRSSCategory(models.Model):
    title = models.CharField(max_length=100)


class FakeRSSItem(models.Model):
    title = models.CharField(max_length=100)
    guid = models.CharField(max_length=100, unique=True)
    date_published = models.DateTimeField(blank=True)
