"""Orchestrates the agents: fetch → curate → summarize → comment → edit."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from .fetchers import fetch_all
from .sources import SOURCES
from .agents import curator, summarizer, commentator, editor, Comment
from .config import client, PERSONAS, TOP_K


def run_pipeline() -> str:
    """Run the full pipeline. Returns the final Markdown brief."""
    today = date.today().isoformat()

    print(f"\n[1/5] Fetching sources...")
    raw_stories = fetch_all(SOURCES)
    print(f"      → {len(raw_stories)} total stories")

    print(f"\n[2/5] Curating top {TOP_K}...")
    top_stories = curator(raw_stories, client, top_k=TOP_K)
    for s in top_stories:
        print(f"      → {s['title'][:70]}")

    print(f"\n[3/5] Summarizing...")
    summarized = [summarizer(s, client) for s in top_stories]

    print(f"\n[4/5] Generating commentary ({len(PERSONAS)} personas in parallel)...")
    comments: dict[str, list[Comment]] = {}
    with ThreadPoolExecutor(max_workers=len(PERSONAS) * 2) as pool:
        for story in summarized:
            futures = {
                pool.submit(commentator, story, persona, client): persona
                for persona in PERSONAS
            }
            comments[story["url"]] = [f.result() for f in futures]

    print(f"\n[5/5] Editor assembling final brief...")
    return editor(summarized, comments, client, date_str=today)
