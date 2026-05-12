"""Fetch stories from RSS sources."""
from typing import TypedDict
import feedparser
from .sources import Source


class Story(TypedDict, total=False):
    title: str
    url: str
    source: str
    raw_summary: str  # raw RSS description / summary
    summary: str | None  # filled by summarizer agent
    score: float | None  # filled by curator agent


def fetch_rss(source: Source) -> list[Story]:
    """Pull entries from a single RSS source."""
    feed = feedparser.parse(source["url"])
    limit = source.get("limit", 10)
    return [
        {
            "title": entry.get("title", "(no title)"),
            "url": entry.get("link", ""),
            "source": source["name"],
            "raw_summary": entry.get("summary", ""),
            "summary": None,
            "score": None,
        }
        for entry in feed.entries[:limit]
    ]


def fetch_all(sources: list[Source]) -> list[Story]:
    """Fetch from every source. Logs failures but doesn't crash the pipeline."""
    stories: list[Story] = []
    for s in sources:
        try:
            fetched = fetch_rss(s)
            stories.extend(fetched)
            print(f"  ✓ {s['name']}: {len(fetched)} stories")
        except Exception as e:
            print(f"  ✗ {s['name']}: {e}")
    return stories
