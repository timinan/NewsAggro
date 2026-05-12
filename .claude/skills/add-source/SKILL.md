---
name: add-source
description: Add a new RSS or Atom feed to the news aggregator pipeline. Walks through URL discovery, category, fetch limits, and a test fetch before wiring it into SOURCES.
---

# Add a news source

Use this when the user wants to pull from a new content source.

## Gather

If the user hasn't specified, ask:
1. **Source name** (e.g., "Stratechery")
2. **Feed URL** — most blogs and Substacks have `/feed`, `/rss`, or `/feed.xml`. Try those first.
3. **Category** — one of `crypto`, `ai`, `pm`, `tech`, `dev`, or a new one if it fits a persistent theme.
4. **Limit** — entries to pull per fetch. Default `10` is usually fine. Use `15-20` for high-volume firehoses like HN, `3-5` for slow weeklies.

## Verify before wiring

Run a one-line parse test to catch broken or empty feeds:

```bash
python -c "import feedparser; f = feedparser.parse('<URL>'); print(len(f.entries), f.feed.get('title', 'no title'))"
```

Expected: entry count > 0, title looks right.

## Wire it in

Append to the `SOURCES` list in `newsaggro/sources.py`. Keep entries grouped by category for readability.

```python
{
    "name": "Stratechery",
    "url": "https://stratechery.com/feed/",
    "category": "tech",
    "limit": 5,
},
```

## Confirm end-to-end

After adding, do a quick smoke test:

```bash
python -c "from newsaggro.fetchers import fetch_rss; from newsaggro.sources import SOURCES; r = fetch_rss(SOURCES[-1]); print(len(r), r[0]['title'])"
```

Then if confidence is high: `python brief.py`.

## When RSS isn't available

1. Look for an Atom feed (often at the same URL).
2. Check if the site has a JSON feed at `/feed.json`.
3. Last resort: write a custom `fetch_<name>` function in `newsaggro/fetchers.py` using `httpx` + `BeautifulSoup`, and call it from `fetch_all`.

Don't add a source you can't verify in under 30 seconds. Slow custom scrapers belong in v2.
