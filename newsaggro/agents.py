"""The agents: curator, summarizer, editor. Stateless functions, one LLM call each.

Uses the OpenAI SDK, which works with Groq (default), Gemini, OpenAI, OpenRouter,
or Ollama via base_url config in `config.py`.
"""
import json
import time
import threading
from openai import OpenAI
from .config import MODEL, EDITOR_MODEL, MIN_CALL_INTERVAL_SECONDS, REQUIRED_CATEGORIES
from .fetchers import Story


# Global throttle to keep us under provider RPM limits.
_throttle_lock = threading.Lock()
_last_call_ts = [0.0]


def _throttle():
    with _throttle_lock:
        now = time.monotonic()
        wait = MIN_CALL_INTERVAL_SECONDS - (now - _last_call_ts[0])
        if wait > 0:
            time.sleep(wait)
        _last_call_ts[0] = time.monotonic()


# ============================================================
# Prompts
# ============================================================

CURATOR_PROMPT = """You are a news curator. From the list of stories below, pick the top {top_k} most interesting and important stories of the day. Dedupe overlapping stories (same news from different outlets). Prioritize stories that are genuinely new, substantive, and likely to matter in a week.

Stories (each has an integer id):
{stories_json}

Return a JSON array of the integer ids of the top {top_k} stories you picked, ordered by importance. Example: [3, 17, 8, 22, 5]. Output the JSON array only, nothing else."""


SUMMARIZER_PROMPT = """Summarize this news story in two forms:

1. "short" — a neutral 2-sentence summary suitable for a card preview. No hype.
2. "detailed" — a 4-6 sentence summary with more context: what specifically happened, who's involved, the relevant numbers, and why it matters. Still neutral, no commentary.

Title: {title}
Source: {source}
Raw content: {raw_summary}

Return strict JSON with exactly two keys: {{"short": "...", "detailed": "..."}}. No markdown code fences, no surrounding text."""


EDITOR_PROMPT = """You are writing a short opening paragraph for a daily news brief. Look at today's stories below and write a single 1-2 sentence intro that captures the main themes. No headlines, no lists, just a clean opener. Neutral tone.

Today's stories:
{stories_summary}

Return only the 1-2 sentence intro paragraph."""


# ============================================================
# Helpers
# ============================================================

def _chat(client: OpenAI, model: str, prompt: str, max_tokens: int) -> str:
    _throttle()
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return (response.choices[0].message.content or "").strip()


def _extract_json_array(text: str) -> list | None:
    """Best-effort extraction of a JSON array from a model response."""
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.lstrip().startswith("json"):
                inner = inner.lstrip()[4:]
            text = inner

    try:
        result = json.loads(text.strip())
        return result if isinstance(result, list) else None
    except json.JSONDecodeError:
        pass

    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            result = json.loads(text[start : end + 1])
            return result if isinstance(result, list) else None
        except json.JSONDecodeError:
            return None
    return None


# ============================================================
# Agents
# ============================================================

def curator(stories: list[Story], client: OpenAI, top_k: int = 7) -> list[Story]:
    """Pick the top_k stories. Guarantees one story from each REQUIRED_CATEGORIES
    (taken as the first/latest from that category's source), then uses the LLM
    to fill the remaining slots from the rest.
    """
    if len(stories) <= top_k:
        return stories

    # Bucket by category
    by_category: dict[str, list[Story]] = {}
    for s in stories:
        cat = s.get("category", "other")
        by_category.setdefault(cat, []).append(s)

    # One required pick per required category (latest = first in feed)
    required_picks: list[Story] = []
    for cat in REQUIRED_CATEGORIES:
        if by_category.get(cat):
            required_picks.append(by_category[cat][0])

    required_urls = {s["url"] for s in required_picks}
    remaining = [s for s in stories if s["url"] not in required_urls]

    n_extras = top_k - len(required_picks)
    if n_extras <= 0:
        return required_picks[:top_k]
    if len(remaining) <= n_extras:
        return required_picks + remaining

    extras = _curate_with_llm(remaining, client, n_extras)
    return required_picks + extras


def _curate_with_llm(stories: list[Story], client: OpenAI, top_k: int) -> list[Story]:
    """LLM picks top_k stories from the given pool. Compact id-based prompt."""
    compact = [
        {"id": i, "title": s["title"], "source": s["source"]}
        for i, s in enumerate(stories)
    ]
    prompt = CURATOR_PROMPT.format(top_k=top_k, stories_json=json.dumps(compact))
    text = _chat(client, MODEL, prompt, max_tokens=512)

    picked_ids = _extract_json_array(text)
    if picked_ids is None:
        print(f"  ⚠ curator returned unparseable response, falling back to first {top_k}")
        return stories[:top_k]

    picked = [
        stories[i]
        for i in picked_ids
        if isinstance(i, int) and 0 <= i < len(stories)
    ]
    if not picked:
        return stories[:top_k]
    return picked[:top_k]


def summarizer(story: Story, client: OpenAI) -> Story:
    """Add both a short and detailed summary to a story."""
    prompt = SUMMARIZER_PROMPT.format(
        title=story["title"],
        source=story["source"],
        raw_summary=story.get("raw_summary", "")[:1500],
    )
    text = _chat(client, MODEL, prompt, max_tokens=600)

    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.lstrip().startswith("json"):
                inner = inner.lstrip()[4:]
            text = inner.strip()

    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
        parsed = json.loads(text)
        story["summary"] = (parsed.get("short", "") or "").strip() or None
        story["detailed_summary"] = (parsed.get("detailed", "") or "").strip() or None
    except json.JSONDecodeError:
        print(f"  ⚠ summarizer JSON parse failed for: {story['title'][:60]}")
        story["summary"] = text.strip()[:300]
        story["detailed_summary"] = None
    return story


def editor(stories: list[Story], client: OpenAI, date_str: str) -> str:
    """Write a short 1-2 sentence intro for the day's brief."""
    lines = [f"- {s['title']} ({s['source']})" for s in stories]
    prompt = EDITOR_PROMPT.format(stories_summary="\n".join(lines))
    return _chat(client, EDITOR_MODEL, prompt, max_tokens=300)
