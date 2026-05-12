"""The five agents. Stateless functions, one LLM call each.

Uses the OpenAI SDK, which works with Gemini (default), Groq, OpenAI, OpenRouter,
and Ollama via base_url config in `config.py`.
"""
import json
import time
import threading
from typing import TypedDict
from openai import OpenAI
from .config import MODEL, EDITOR_MODEL, MIN_CALL_INTERVAL_SECONDS
from .fetchers import Story

# Global throttle to keep us under provider RPM limits.
_throttle_lock = threading.Lock()
_last_call_ts = [0.0]


def _throttle():
    """Sleep just enough to keep calls spaced by MIN_CALL_INTERVAL_SECONDS."""
    with _throttle_lock:
        now = time.monotonic()
        wait = MIN_CALL_INTERVAL_SECONDS - (now - _last_call_ts[0])
        if wait > 0:
            time.sleep(wait)
        _last_call_ts[0] = time.monotonic()


class Comment(TypedDict):
    persona: str
    text: str


# ============================================================
# Prompts
# ============================================================

CURATOR_PROMPT = """You are a news curator. From the list of stories below, pick the top {top_k} most interesting and important stories of the day. Dedupe overlapping stories (same news from different outlets). Prioritize stories that are genuinely new, substantive, and likely to matter in a week.

Stories:
{stories_json}

Return a JSON array of the URLs of the top {top_k} stories you picked, ordered by importance. Just the JSON array, nothing else."""


SUMMARIZER_PROMPT = """Write a neutral 2-sentence summary of this news story. No opinion, no commentary, no hype language. Just the facts.

Title: {title}
Source: {source}
Raw summary: {raw_summary}

Return only the 2-sentence summary."""


COMMENTATOR_PROMPTS = {
    "Builder": """You are a founder who's shipped products in this space. React to this story in 1-2 sentences. What does this mean for someone building right now? Be specific and pragmatic. No hype.

Story: {title}
Summary: {summary}""",

    "Skeptic": """You are a sharp skeptic who's seen many hype cycles. React to this story in 1-2 sentences. What's the dumb interpretation people are missing? What might not pan out? Be sharp, not snarky.

Story: {title}
Summary: {summary}""",

    "Degen": """You are a crypto degenerate trader with too much screen time. React to this story in 1-2 sentences. What's the trade? Who wins, who loses, who's about to get rugged? Be funny but specific.

Story: {title}
Summary: {summary}""",
}


EDITOR_PROMPT = """You are the editor of a daily news brief. Assemble the following stories and commentary into a clean, readable Markdown document. Add a short (1-2 sentence) opening that sets the tone for today's brief based on the themes you see. Keep everything tight.

Today's stories with commentary:
{stories_json}

Return only the final Markdown brief. Start with a level-1 heading like `# Daily Brief — {date}`."""


# ============================================================
# Helper
# ============================================================

def _chat(client: OpenAI, model: str, prompt: str, max_tokens: int) -> str:
    """One-shot chat completion. Returns the text content."""
    _throttle()
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return (response.choices[0].message.content or "").strip()


def _extract_json_array(text: str) -> list | None:
    """Best-effort extraction of a JSON array from a model response.
    Handles code fences, leading prose, and trailing prose.
    """
    # Strip code fences
    if "```" in text:
        # Try to grab the content between the first pair of fences
        parts = text.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.lstrip().startswith("json"):
                inner = inner.lstrip()[4:]
            text = inner

    # Try direct parse
    try:
        result = json.loads(text.strip())
        return result if isinstance(result, list) else None
    except json.JSONDecodeError:
        pass

    # Try to grab everything between first [ and last ]
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

def curator(stories: list[Story], client: OpenAI, top_k: int = 5) -> list[Story]:
    """Pick the top_k most interesting stories from the raw fetched list."""
    if len(stories) <= top_k:
        return stories

    compact = [
        {"url": s["url"], "title": s["title"], "source": s["source"]}
        for s in stories
    ]
    prompt = CURATOR_PROMPT.format(top_k=top_k, stories_json=json.dumps(compact, indent=2))
    text = _chat(client, MODEL, prompt, max_tokens=4096)

    picked_urls = _extract_json_array(text)
    if picked_urls is None:
        print(f"  ⚠ curator returned unparseable response, falling back to first {top_k} stories")
        print(f"     raw: {text[:300]!r}")
        return stories[:top_k]

    by_url = {s["url"]: s for s in stories}
    picked = [by_url[u] for u in picked_urls if u in by_url]
    # Fallback if the model invented URLs
    if not picked:
        print(f"  ⚠ curator picks didn't match any input URLs, using first {top_k}")
        return stories[:top_k]
    return picked[:top_k]


def summarizer(story: Story, client: OpenAI) -> Story:
    """Add a neutral 2-sentence summary to a story."""
    prompt = SUMMARIZER_PROMPT.format(
        title=story["title"],
        source=story["source"],
        raw_summary=story.get("raw_summary", "")[:1500],
    )
    story["summary"] = _chat(client, MODEL, prompt, max_tokens=256)
    return story


def commentator(story: Story, persona: str, client: OpenAI) -> Comment:
    """Generate a persona-driven reaction to a story."""
    template = COMMENTATOR_PROMPTS.get(persona)
    if not template:
        raise ValueError(f"Unknown persona: {persona}. Add a prompt in COMMENTATOR_PROMPTS.")

    prompt = template.format(
        title=story["title"],
        summary=story.get("summary") or story.get("raw_summary", "")[:500],
    )
    text = _chat(client, MODEL, prompt, max_tokens=256)
    return {"persona": persona, "text": text}


def editor(
    stories: list[Story],
    comments: dict[str, list[Comment]],
    client: OpenAI,
    date_str: str,
) -> str:
    """Assemble the final Markdown brief."""
    payload = []
    for s in stories:
        payload.append({
            "title": s["title"],
            "source": s["source"],
            "url": s["url"],
            "summary": s.get("summary"),
            "comments": comments.get(s["url"], []),
        })

    prompt = EDITOR_PROMPT.format(
        stories_json=json.dumps(payload, indent=2),
        date=date_str,
    )
    return _chat(client, EDITOR_MODEL, prompt, max_tokens=8192)
