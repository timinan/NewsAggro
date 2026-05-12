# NewsAggro — Claude Code Context

This is a one-day multi-agent news aggregator project. Daily Markdown brief built with five Claude agents in a pipeline.

## Project goal

Ship something demo-able in one day that:
- Uses real Anthropic API calls (no mocked-out LLM)
- Has a multi-agent shape (5 agents, role-play personas)
- Produces a daily brief the user would actually read
- Is small enough to fully understand and walk through in an interview

## Architecture

```
RSS Sources → Fetchers → Curator → Summarizer → Commentators (parallel) → Editor → Markdown
```

Each agent is a stateless function in `newsaggro/agents.py`. Pipeline orchestration is in `newsaggro/pipeline.py`. Output writing is in `newsaggro/output.py`.

## Where things live

| Concern | File |
|---|---|
| Source list | `newsaggro/sources.py` |
| Fetch logic | `newsaggro/fetchers.py` |
| Agent functions + prompts | `newsaggro/agents.py` |
| Pipeline orchestration | `newsaggro/pipeline.py` |
| Output file writing | `newsaggro/output.py` |
| Config (model, personas, top_k) | `newsaggro/config.py` |
| CLI entrypoint | `brief.py` |

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env  # add ANTHROPIC_API_KEY
python brief.py
```

## Design principles

- **Agents as functions, not classes.** Easy to swap, easy to read.
- **Personas as data.** Adding a new persona = adding a string to `PERSONAS`. No new class.
- **One Claude call per agent.** If you want a critic/refiner loop, do it in `pipeline.py`, not inside an agent.
- **Fail loud.** Don't wrap Anthropic errors in try/except during the build. Crashes teach.
- **No premature abstractions.** Resist the urge to introduce a BaseAgent class or a plugin system. This ships in one day.

## Skills available

When working on this project, prefer the project skills in `.claude/skills/`:
- `/add-source` for adding RSS feeds
- `/new-agent` for designing new agent roles
- `/tune-prompt` for iterating on prompts
- `/run-brief` for executing the pipeline
- `/demo-day` for wrapping the project for interviews

## Stack

- **Python 3.10+**
- **Anthropic SDK** (`anthropic`) for Claude
- **feedparser** for RSS
- **python-dotenv** for `.env` loading

## Models

Default: `claude-sonnet-4-6` for the worker agents (curator, summarizer, commentators).
Default: `claude-opus-4-7` for editor (it gets the highest-leverage synthesis call).

Both are overridable in `newsaggro/config.py`.

## Not in scope

- Database, persistence beyond Markdown files
- Web UI, dashboards
- Authentication, multi-user
- Email/Slack delivery (could be a v2 stretch)
- Tests beyond smoke tests (this is a portfolio prototype)
