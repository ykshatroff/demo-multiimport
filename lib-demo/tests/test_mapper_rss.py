from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from django.db import models

from mapper.rss import RSSMapper
from tests.models import FakeRSSAuthor, FakeRSSCategory, FakeRSSItem
from unittest.mock import patch

SAMPLE_RSS = """\
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
    <channel>
        <title>Feed #11211</title>
        <pubDate>Mon, 21 May 2018 21:58:52 +0300</pubDate>
        <item>
            <title>An Ship, Demolished,</title>
            <description>named The as rescued to of Ford alien the hope they the in named declines.</description>
            <pubDate>Mon, 21 May 2018 21:58:52 +0300</pubDate>
            <guid>http://localhost:18000/feed/11211/#an%20ship%2C%20demolished%2C</guid>
            <author>Ford Prefect</author>
            <category>Solar System</category>
            <category>Hitchhiking</category>
            <category>Betelgeuse</category>
        </item>
    </channel>
</rss>
""".encode()


def test_mapper_init():
    mapper = RSSMapper(FakeRSSItem, author_model=FakeRSSAuthor, category_model=FakeRSSCategory)
    assert mapper.model is FakeRSSItem
    assert mapper.author_model is FakeRSSAuthor
    assert mapper.category_model is FakeRSSCategory


def test_mapper_process_string():
    mapper = RSSMapper(FakeRSSItem, author_model=FakeRSSAuthor, category_model=FakeRSSCategory)
    with patch.object(mapper, "process") as process:
        result = mapper.process_string(SAMPLE_RSS)


def test_mapper_process_string_not_modified():
    mapper = RSSMapper(FakeRSSItem, author_model=FakeRSSAuthor, category_model=FakeRSSCategory)
    with patch.object(mapper, "process") as process:
        result = mapper.process_string(SAMPLE_RSS, if_modified_since=datetime(2018, 5, 22).astimezone(None))
        assert not process.called
