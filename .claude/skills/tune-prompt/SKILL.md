---
name: tune-prompt
description: Iterate on an agent's prompt. Capture baseline output, propose a revision, A/B compare, keep the winner.
---

# Tune an agent's prompt

Use this when an agent's output is wrong, stale, off-voice, or just bland.

## Step 1: Identify the prompt

All prompts are at the top of `newsaggro/agents.py` as module-level constants:
- `CURATOR_PROMPT`
- `SUMMARIZER_PROMPT`
- `COMMENTATOR_PROMPTS` (a dict, one entry per persona)
- `EDITOR_PROMPT`

If the agent uses prompts elsewhere, refactor them up to module-level first. Easier to iterate when all prompts live together.

## Step 2: Capture baseline

Run the pipeline once with the current prompt and save the output for comparison:

```bash
python brief.py
cp briefs/brief_$(date +%F).md briefs/baseline.md
```

## Step 3: State the gap

Before changing anything, write down (out loud or in a comment) what's wrong:
- Too verbose? Add explicit length limits.
- Wrong voice? Add an example of the desired voice.
- Hallucinating? Add "If you don't know, say so."
- Repetitive across stories? Add "Vary your sentence structure and openings."
- Bland personas? Sharpen the character. "Builder" → "A founder who's been burned three times by hype cycles."

## Step 4: Propose the revision

Show the user the new prompt as a diff before applying. Explain what changed and why in one sentence.

## Step 5: Re-run and compare

```bash
python brief.py
cp briefs/brief_$(date +%F).md briefs/candidate.md
```

Diff or read both side-by-side. Keep the winner. Delete or rename the loser.

## Don't

- **Tune two agents at once.** Isolate the variable.
- **Change prompt and model together.** Same reason.
- **Delete old prompts immediately.** Comment them out at first so you can revert.
- **Spend more than 3 iterations on one agent.** If it's not converging, the issue is upstream (bad input data, wrong agent role, model too small).

## When stuck

If iteration isn't converging, try one of:
- Switch from `MODEL` to `EDITOR_MODEL` (Opus) for that agent
- Add a few-shot example directly in the prompt
- Break the agent into two (e.g. extract → format)
