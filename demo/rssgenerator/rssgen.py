import random
from datetime import datetime, timedelta
from urllib.parse import quote

from aiohttp import web
from xml.dom import minidom
import logging
from demo.settings import RSS_DATE_FORMAT


logger = logging.getLogger(__name__)

AUTHORS = [
    "Arthur Dent",
    "Ford Prefect",
    "Zaphod Beeblebrox",
    "Tricia 'Trillian' McMillan",
    "Marvin",
]

CATEGORIES = [
    "Hitchhiking",
    "Space Invaders",
    "Solar System",
    "Betelgeuse",
    "The Ultimate Answer",
]

# Some text from Wikipedia, used for generation
TEXT = """
The book begins with council workmen arriving at Arthur Dent's house. 
They wish to demolish his house in order to build a bypass.

Arthur's best friend, Ford Prefect, arrives, warning him of the end of the world. 
Ford is revealed to be an alien who had come to Earth to research it for the titular Hitchhiker's Guide to the Galaxy, 
an enormous work providing information about every planet and place in the universe. 
The two head to a pub, where the locals question Ford's knowledge of the Apocalypse. An alien race, known as Vogons, 
show up to demolish Earth in order to build a bypass for an intergalactic highway. Arthur and Ford manage to get onto
 the Vogon ship just before Earth is demolished, where they are forced to listen to horrible Vogon poetry as a form of 
 torture. Arthur and Ford are ordered to say how much they like the poetry in order to avoid being thrown out of 
 the airlock, and while Ford finds listening to be painful, Arthur believes it to be genuinely good, 
 since human poetry is apparently even worse.

Arthur and Ford are then placed into the airlock and jettisoned into space, only to be rescued by 
Zaphod Beeblebrox's ship, the Heart of Gold. Zaphod, a semi-cousin of Ford, is the President of the Galaxy, 
and is accompanied by a depressed robot named Marvin and a human woman by the name of Trillian. 
The five embark on a journey to find the legendary planet known as Magrathea, known for selling luxury planets.
 Once there, they are taken into the planet's centre by a man named Slartibartfast. There, they learn that a 
 supercomputer named Deep Thought, who determined the ultimate answer to life, the universe, and everything 
 to be the number 42, created Earth as an even greater computer to calculate the question to which 42 is the answer.

Trillian's mice, actually part of the group of sentient and hyper-intelligent superbeings that had Earth created 
in the first place, reject the idea of building a second Earth to redo the process, and offer to buy Arthur's brain
 in the hope that it contains the question, leading to a fight when he declines. Zaphod saves Arthur when the brain 
 is about to be removed, and the group decides to go to The Restaurant at the 
 End of the Universe."""

WORDS = [w for w in TEXT.replace("\n", " ").split(" ") if w]


FEEDS = {}
BASE_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
    <channel>
        <title>Feed #{number}</title>
        <pubDate>{date}</pubDate>
    </channel>
</rss>
"""

RSS_CONTENT_TYPE = "application/rss+xml"


def generate_rss_item(xml_doc: minidom.Document, pub_date: datetime, self_url: str):
    author = random.choice(AUTHORS)
    categories = random.sample(CATEGORIES, random.randint(0, 3))

    item_node = xml_doc.createElement("item")

    title = " ".join([w.capitalize() for w in random.sample(WORDS, random.randint(2, 5))])
    title_node = xml_doc.createElement("title")
    title_node.appendChild(xml_doc.createTextNode(title))
    item_node.appendChild(title_node)

    descr = " ".join(random.sample(WORDS, random.randint(10, 50)))
    descr_node = xml_doc.createElement("description")
    descr_node.appendChild(xml_doc.createTextNode(descr))
    item_node.appendChild(descr_node)

    date_node = xml_doc.createElement("pubDate")
    pub_date = pub_date - timedelta(seconds=random.randint(0, 86400*30))
    date_node.appendChild(xml_doc.createTextNode(pub_date.strftime(RSS_DATE_FORMAT)))
    item_node.appendChild(date_node)

    guid_node = xml_doc.createElement("guid")
    encoded_link = quote(title.lower())
    guid_node.appendChild(xml_doc.createTextNode(f"{self_url}#{encoded_link}"))
    item_node.appendChild(guid_node)

    author_node = xml_doc.createElement("author")
    author_node.appendChild(xml_doc.createTextNode(author))
    item_node.appendChild(author_node)

    for category in categories:
        node = xml_doc.createElement("category")
        node.appendChild(xml_doc.createTextNode(category))
        item_node.appendChild(node)

    return item_node


async def rss_generator(request: web.Request):
    feed_number = request.match_info['feed']
    logger.debug("Got request for feed #%s", feed_number)

    self_url = str(request.url)
    now = datetime.now().astimezone(None)
    pub_date = now.strftime(RSS_DATE_FORMAT)
    try:
        xml = FEEDS[feed_number]  # type: minidom.Document
    except KeyError:
        xml = FEEDS[feed_number] = minidom.parseString(
            BASE_TEMPLATE.format(number=feed_number, date=pub_date)
        )

        channel_node = xml.getElementsByTagName('channel')[0]
        for item in range(random.randint(1, 5)):
            channel_node.appendChild(generate_rss_item(xml, now, self_url))
    else:
        channel_node = xml.getElementsByTagName('channel')[0]
        feed_pub_date_node = channel_node.getElementsByTagName('pubDate')[0]
        feed_pub_date = datetime.strptime(feed_pub_date_node.childNodes[0].data, RSS_DATE_FORMAT).astimezone(None)
        print("Now", now, ", feed pub date", feed_pub_date, ", delta", now - feed_pub_date)
        if (now - feed_pub_date).seconds > 60:
            channel_node.appendChild(generate_rss_item(xml, now, self_url))  # create a new news item
            feed_pub_date_node.childNodes[0].nodeValue = pub_date  # update channel publish date

    return web.Response(body=xml.toprettyxml(encoding="utf-8"),
                        content_type=RSS_CONTENT_TYPE)
