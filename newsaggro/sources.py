"""RSS source registry. Add new sources here, or via /add-source."""
from typing import TypedDict


class Source(TypedDict, total=False):
    name: str
    url: str
    category: str  # crypto, ai, pm, tech, dev
    limit: int


SOURCES: list[Source] = [
    {
        "name": "The Defiant",
        "url": "https://thedefiant.io/feed",
        "category": "crypto",
        "limit": 10,
    },
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "category": "crypto",
        "limit": 10,
    },
    {
        "name": "Latent Space",
        "url": "https://www.latent.space/feed",
        "category": "ai",
        "limit": 10,
    },
    {
        "name": "Hacker News Front",
        "url": "https://hnrss.org/frontpage",
        "category": "tech",
        "limit": 15,
    },
    {
        "name": "Lenny's Newsletter",
        "url": "https://www.lennysnewsletter.com/feed",
        "category": "pm",
        "limit": 5,
    },
]
