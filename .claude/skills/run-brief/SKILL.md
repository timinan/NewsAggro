---
name: run-brief
description: Run the news pipeline. Covers the default run, debug-mode runs (single source, single persona, dry-run), and common failure modes.
---

# Run the daily brief

Use this when the user wants to execute the pipeline or debug a stuck run.

## Default run

```bash
python brief.py
```

Output: `briefs/brief_YYYY-MM-DD.md`. Overwrites if today's already exists.

## Debug-mode runs

For faster iteration, hack `pipeline.py` or `config.py` temporarily:

| Goal | How |
|---|---|
| Test one source only | Edit `SOURCES` in `sources.py`, comment out the rest |
| Test one persona only | Set `PERSONAS = ["Builder"]` in `config.py` |
| Skip Claude calls (fetch only) | Run `python -c "from newsaggro.fetchers import fetch_all; from newsaggro.sources import SOURCES; print(len(fetch_all(SOURCES)))"` |
| Smaller, faster runs | Set `TOP_K = 2` in `config.py` |
| Cheaper iteration | Set `EDITOR_MODEL = "claude-haiku-4-5-20251001"` temporarily |

When adding flags to `brief.py` is worth it (more than 3 manual edits), add `argparse`:

```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--top-k", type=int)
parser.add_argument("--persona", help="Limit to one persona")
parser.add_argument("--source", help="Limit to one source")
parser.add_argument("--dry-run", action="store_true", help="Fetch only, no LLM calls")
```

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `anthropic.AuthenticationError` | `.env` missing or wrong key | Check `.env`, re-run |
| Source returns 0 stories | Feed URL changed or rate-limited | `python -c "import feedparser; print(feedparser.parse('<URL>'))"` to inspect |
| Curator returns wrong stuff | JSON parse fail (model returned prose) | Add stricter "return only a JSON array" to `CURATOR_PROMPT` |
| Personas all sound the same | Prompt differentiation too weak | Use `/tune-prompt` to sharpen each persona |
| Editor brief is too long | `max_tokens` cap or prompt limit | Add explicit length target to `EDITOR_PROMPT` |
| Hangs forever | RSS source timing out | Add `timeout=10` to `feedparser.parse` (it actually doesn't support this — wrap in `httpx` instead) |

## Cost watch

A typical run with 5 stories × 3 personas × current models is ~10-20¢. Keep an eye on the Anthropic dashboard during iteration loops.
