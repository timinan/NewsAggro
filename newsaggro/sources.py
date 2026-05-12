"""RSS source registry. Add new sources here, or via /add-source.

Each source has a category. Categories listed in REQUIRED_CATEGORIES (config.py)
are guaranteed at least one story in the daily brief — the curator picks the
remaining slots from any category.
"""
from typing import TypedDict


class Source(TypedDict, total=False):
    name: str
    url: str
    category: str  # arsenal, canada, vancouver, ai, crypto, tech, pm
    limit: int


SOURCES: list[Source] = [
    # Required categories (guaranteed slots in the brief)
    {
        "name": "BBC Sport — Arsenal",
        "url": "https://feeds.bbci.co.uk/sport/football/teams/arsenal/rss.xml",
        "category": "arsenal",
        "limit": 10,
    },
    {
        "name": "CBC News — Top Stories",
        "url": "https://www.cbc.ca/webfeed/rss/rss-topstories",
        "category": "canada",
        "limit": 10,
    },
    {
        "name": "Daily Hive — Vancouver",
        "url": "https://dailyhive.com/feed/vancouver",
        "category": "vancouver",
        "limit": 10,
    },

    # Curator-picked fillers
    {
        "name": "Latent Space",
        "url": "https://www.latent.space/feed",
        "category": "ai",
        "limit": 10,
    },
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "category": "crypto",
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
