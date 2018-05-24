import logging
from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.db import models
from aiohttp import ClientSession
from asyncio import get_event_loop, gather, sleep

from demo.models import DataSource
from demo.rssnews.models import Author, Category, Item
from mapper.rss import RSSMapper


logger = logging.getLogger(__name__)


async def fetch_source(session: ClientSession, url: str):
    logger.debug("Fetching %s", url)
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.text()
            logger.error("Failed to fetch url %s", url)
    except:
        logger.exception("Failed to fetch url %s", url)


async def fetch_all(loop, sources: list):
    async with ClientSession(loop=loop) as session:
        return await gather(*[
            fetch_source(session, source.url)
            for source in sources
        ])


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--infinite', dest='infinite', action='store_true',
                            help="Run in a loop until Ctrl-C is pressed")
        parser.add_argument('-t', '--timeout', type=int, default=10, dest='timeout',
                            help="If --infinite, specify a timeout between polling sources")

    def handle(self, *args, **options):
        print(options)
        infinite = options['infinite']
        timeout = options['timeout']
        logger.debug("Starting aggregation %s", 'until Ctrl-C is pressed' if infinite else 'once')

        mapper = RSSMapper(model=Item, author_model=Author, category_model=Category)

        sources = list(DataSource.objects.all())

        if not sources:
            logger.error("No sources configured. Exiting")
            return

        loop = get_event_loop()

        while 1:

            results = loop.run_until_complete(fetch_all(loop, sources))

            now = datetime.now().astimezone(None)
            sources_to_fetch = [
                source for source in sources
                if (source.last_successful_update and
                    source.last_successful_update + timedelta(seconds=source.poll_frequency) < now)
            ]

            for i, source in enumerate(sources_to_fetch):  # type source: DataSource
                source.poll_count = models.F('poll_count') + 1
                fetched = results[i]
                if fetched is not None:
                    try:
                        mapper.process_string(fetched, if_modified_since=source.last_successful_update)
                    except:
                        logger.exception("Failed to process source %s [%s]", source.title, source.url)
                    else:
                        source.last_successful_update = datetime.now().astimezone(None)
                source.save()

            if infinite:
                logger.debug("Sleeping for %ss", timeout)
                loop.run_until_complete(sleep(timeout))
                # TODO add option to re-read sources if necessary
            else:
                break

        loop.close()
