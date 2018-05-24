import logging
from datetime import datetime
from typing import Type, List

import feedparser
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

from mapper.base import MapperBase

logger = logging.getLogger(__name__)

try:
    RSS_DATE_FORMAT = settings.RSS_DATE_FORMAT
except AttributeError:
    RSS_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z"


class RSSMapper(MapperBase):
    author_model = None
    category_model = None

    unique_fields = ['guid']

    def __init__(self, model: Type[models.Model], author_model: Type[models.Model], category_model: Type[models.Model]):
        super().__init__(model)
        self.author_model = author_model
        self.category_model = category_model

    def transform_date_published(self, data, field):
        date = data.published
        if not date:
            return None
        try:
            return datetime.strptime(date, settings.DATE_FORMAT)
        except:
            return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z").astimezone(None)

    def transform_author(self, data, field):
        value = self.get_value(data, field)
        author_obj, _ = self.author_model.objects.get_or_create(name=value)
        return author_obj

    def transform_categories(self, data, field):
        try:
            value = self.get_value(data, field, 'tags')
        except ValidationError:
            return []

        categories = []
        for category_dict in value:
            category_title = category_dict['term']
            # TODO: optimize, using filter()
            # Mysql, Postgresql 9.5+ can insert all objects in one query and make use of ON CONFLICT
            # Postgresql can take advantage of INSERT RETURNING
            category_obj, _ = self.category_model.objects.get_or_create(title=category_title)
            categories.append(category_obj)
        return categories

    def process_entry(self, data: dict):
        instance = super(RSSMapper, self).process_entry(data)
        logger.debug(f"Instance: title '{instance.title}', ID {instance.id}")
        return instance

    def process_string(self, text, if_modified_since: datetime = None) -> List[models.Model]:
        """

        :param text:
        :param if_modified_since: skip processing if source not modified after this time
        :return: list of entries processed
        """
        try:
            text = text.encode()
        except AttributeError:
            pass
        feed = feedparser.parse(text)
        if if_modified_since is not None and feed.feed.published:
            pub_date = datetime.strptime(feed.feed.published, RSS_DATE_FORMAT).astimezone(None)
            if pub_date < if_modified_since:
                logger.debug("Skipping feed as not modified: %s", feed['feed']['title'])
                return []
        logger.debug("Saving feed: %s", feed['feed']['title'])
        return self.process(feed.entries)

