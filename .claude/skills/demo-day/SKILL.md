---
name: demo-day
description: Wrap the project for interview demos. Captures a representative brief, updates the README, drafts the demo narrative, and assembles talking points.
---

# Demo day — capture the artifact

Use this at the end of the build (or whenever the project is interview-ready).

## Outputs needed

1. **One representative brief** in `briefs/example.md` — a clean, recent run with no embarrassing model output
2. **README** updated with: short pitch, screenshot or example excerpt, architecture diagram, what was hard
3. **Demo video script** (60-90 seconds) — see template below
4. **Talking points** for the interview — what to lead with, what to emphasize, what NOT to over-explain

## The narrative arc (use this in interviews)

> "I wanted hands-on multi-agent experience to close the AI-shipping gap on my resume, so I gave myself one day to ship something I'd actually use. I built a 5-agent news brief: fetchers pull from my RSS feeds, a curator dedupes and ranks the top 5 stories, a summarizer writes neutral 2-sentence summaries, three role-play personas (Builder, Skeptic, Degen) react to each story in parallel, and an editor assembles the final Markdown."
>
> "What I learned in one day: [pick one or two from below]"
>
> "If I had another day, I'd add: [one credible next step]"

## "What I learned" candidates (pick 1-2 real ones)

- The curator hallucinated URLs that weren't in its input. Fixed by post-validating against the input set.
- Personas drifted into the same voice. Fixed by anchoring each persona to a sharper character description with concrete priors.
- Editor occasionally rewrote the summaries the summarizer just produced. Fixed by giving the editor an explicit "don't rewrite, just arrange" instruction.
- Parallel commentator calls cut runtime roughly 3x but blew through rate limits on burst. Added simple semaphore.
- Cheap-model curator missed obvious dedupes (e.g. The Verge and TechCrunch covering the same launch). Upgraded only the curator to Opus.

The "what I learned" is the most important part of the demo. Pick real ones from your build, not placeholders.

## Demo video script (60-90 sec)

```
0:00-0:10  "I built a one-day multi-agent news aggregator. Five agents in a pipeline. Let me show you."
0:10-0:25  Run `python brief.py`. Talk over the agent prints as they appear.
0:25-0:45  Open today's brief. Walk through one story end-to-end: source, summary, 3 persona reactions.
0:45-1:10  Quick code tour: agents.py (point at one prompt), pipeline.py (point at the parallel block).
1:10-1:30  "Here's what surprised me [pick one]. If I had more time, I'd [one credible extension]."
```

Record on Loom or screen capture. Don't over-edit. The point is the work, not the production.

## Talking points

**Lead with:**
- Multi-agent architecture (5 agents, pipeline + parallel work)
- Hands-on Anthropic SDK and tool/role design
- Real LLM in production (cost-aware: ~10-20¢ per run)

**Emphasize if asked:**
- One Claude call per agent — easy to reason about, easy to swap models
- Editor on Opus for the synthesis call, workers on Sonnet for cost
- Personas as data, not classes — adding a new voice is a 2-line change

**Don't over-explain:**
- Feedparser. It's plumbing.
- The Markdown output. Obvious.
- Why no DB/auth/web UI. "It's a one-day prototype" is the whole answer.

## Resume bullet (one option)

> Built a 5-agent news aggregator (Python + Anthropic SDK) in a day to learn multi-agent orchestration end-to-end. Pipeline includes a curator that dedupes and ranks stories, a summarizer, three role-play commentator personas running in parallel, and an editor that synthesizes the final brief. Use it daily.

Adjust voice to match the rest of your resume.
