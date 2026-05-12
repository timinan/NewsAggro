# NewsAggro

A daily news brief built as a one-day multi-agent Claude project.

Five agents in a pipeline: fetchers pull stories from your RSS sources, a curator dedupes and ranks the top N, a summarizer writes neutral 2-sentence summaries, three commentator personas (Builder, Skeptic, Degen) react in parallel, and an editor assembles a Markdown brief.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env: add your ANTHROPIC_API_KEY
python brief.py
```

Output lands in `briefs/brief_YYYY-MM-DD.md`.

## Architecture

```
RSS sources → Fetcher → Curator → Summarizer → Commentators (parallel) → Editor → brief.md
```

| Component | What it does | File |
|---|---|---|
| Fetcher | Pull stories from RSS feeds | `newsaggro/fetchers.py` |
| Curator | Dedupe + rank top K stories | `newsaggro/agents.py` |
| Summarizer | Neutral 2-sentence summary | `newsaggro/agents.py` |
| Commentator | Persona-driven reaction | `newsaggro/agents.py` |
| Editor | Assemble final Markdown | `newsaggro/agents.py` |
| Pipeline | Orchestrate the flow | `newsaggro/pipeline.py` |

## Customize

- **Sources** — `newsaggro/sources.py`
- **Personas** — `PERSONAS` in `newsaggro/config.py`
- **Story count** — `TOP_K` in `newsaggro/config.py`
- **Model** — `MODEL` in `newsaggro/config.py`

## Claude Code skills

This repo includes `.claude/skills/` for repeated tasks while building:

- `/add-source` — add a new RSS source
- `/new-agent` — design a new agent role
- `/tune-prompt` — iterate on an agent's prompt
- `/run-brief` — run the pipeline
- `/demo-day` — capture the demo artifact

## Design principles

- One-day build. No DB, no auth, no web UI.
- Agents are stateless functions, not classes.
- Personas are data (strings), not subclasses.
- Fail loud during development.
