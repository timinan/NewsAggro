"""Fetch stories from RSS sources and pull og:image for each."""
import re
from typing import TypedDict
import feedparser
import httpx
from .sources import Source


class Story(TypedDict, total=False):
    title: str
    url: str
    source: str
    category: str  # arsenal, canada, vancouver, ai, crypto, tech, pm
    raw_summary: str  # raw RSS description / summary
    summary: str | None  # short summary, filled by summarizer
    detailed_summary: str | None  # longer paragraph, filled by summarizer
    image_url: str | None  # og:image scraped from the article page
    score: float | None  # filled by curator (currently unused)


_FEED_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) NewsAggro/1.0"


def fetch_rss(source: Source) -> list[Story]:
    """Pull entries from a single RSS source."""
    # Some publishers (e.g. CBC) reject the default urllib User-Agent.
    feed = feedparser.parse(source["url"], agent=_FEED_USER_AGENT)
    limit = source.get("limit", 10)
    category = source.get("category", "other")
    return [
        {
            "title": entry.get("title", "(no title)"),
            "url": entry.get("link", ""),
            "source": source["name"],
            "category": category,
            "raw_summary": entry.get("summary", ""),
            "summary": None,
            "detailed_summary": None,
            "image_url": None,
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


# ============================================================
# og:image scraper
# ============================================================

_OG_PATTERNS = [
    re.compile(rb'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE),
    re.compile(rb'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image(?::secure_url)?["\']', re.IGNORECASE),
    re.compile(rb'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE),
    re.compile(rb'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']', re.IGNORECASE),
]

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NewsAggro/1.0)",
    "Accept": "text/html,application/xhtml+xml",
}


def fetch_og_image(url: str, timeout: float = 6.0) -> str | None:
    """Fetch the article page and extract its og:image (or twitter:image fallback)."""
    if not url:
        return None
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout, headers=_HEADERS) as client:
            r = client.get(url)
            body = r.content[:250_000]
            for pattern in _OG_PATTERNS:
                m = pattern.search(body)
                if m:
                    image_url = m.group(1).decode("utf-8", errors="ignore").strip()
                    image_url = image_url.replace("&amp;", "&")
                    return image_url
    except Exception:
        return None
    return None
