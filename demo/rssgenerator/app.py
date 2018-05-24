import logging
from argparse import ArgumentParser
from logging.config import dictConfig

from demo import settings
dictConfig(settings.LOGGING)  # NOQA

from aiohttp import web
from demo.rssgenerator.rssgen import rss_generator

logger = logging.getLogger(__name__)
logger.debug("Starting RSS generator application")


def run():
    app = web.Application()
    app.router.add_get("/feed/{feed:\d+}/", rss_generator)
    return app


if __name__ == '__main__':
    parser = ArgumentParser(description='Start RSS Feed Generator')
    parser.add_argument('-p', '--port', type=int, default=18000,
                        help='HTTP port (default: 18000)')

    args = parser.parse_args()
    web.run_app(run(), port=args.port)
