"""Orchestrates the agents: fetch → curate → og:images → summarize → editor intro."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import TypedDict
from .fetchers import fetch_all, fetch_og_image, Story
from .sources import SOURCES
from .agents import curator, summarizer, editor
from .config import client, TOP_K


class PipelineResult(TypedDict):
    intro: str
    stories: list[Story]
    date: str


def run_pipeline() -> PipelineResult:
    """Run the full pipeline. Returns the intro + curated/summarized stories."""
    today = date.today().isoformat()

    print(f"\n[1/5] Fetching sources...")
    raw_stories = fetch_all(SOURCES)
    print(f"      → {len(raw_stories)} total stories")

    print(f"\n[2/5] Curating top {TOP_K}...")
    top_stories = curator(raw_stories, client, top_k=TOP_K)
    for s in top_stories:
        print(f"      → [{s.get('category', '?')}] {s['title'][:70]}")

    print(f"\n[3/5] Fetching og:images (parallel)...")
    with ThreadPoolExecutor(max_workers=len(top_stories)) as pool:
        images = list(pool.map(lambda s: fetch_og_image(s["url"]), top_stories))
    for story, img in zip(top_stories, images):
        story["image_url"] = img

    print(f"\n[4/5] Summarizing (short + detailed)...")
    summarized = [summarizer(s, client) for s in top_stories]

    print(f"\n[5/5] Editor writing intro...")
    intro = editor(summarized, client, date_str=today)

    return {
        "intro": intro,
        "stories": summarized,
        "date": today,
    }
