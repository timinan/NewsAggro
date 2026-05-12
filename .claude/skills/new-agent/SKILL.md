---
name: new-agent
description: Design and add a new agent (e.g., a Translator, a Fact-checker, a new commentator persona) to the pipeline. Settles role, position, I/O shape, and prompt voice before writing code.
---

# Add or modify a pipeline agent

Use this when the user wants to add a brand-new agent or significantly change an existing one.

## Settle these before writing code

1. **Role.** What does this agent specifically do? One sentence.
2. **Position in pipeline.** Before/after which existing agent? Or parallel to one (like commentators)?
3. **Input shape.** What does it receive? Single Story? List of Story? Story + context?
4. **Output shape.** Same Story (mutated)? A separate Comment dict? Plain text?
5. **Persona / voice.** Neutral and analytical, or in-character? Tightly templated or freer?
6. **Token budget.** How many tokens of output? Set `max_tokens` accordingly to keep cost bounded.

## Three common shapes

| Shape | Example | Where it lives |
|---|---|---|
| **Transform a story in place** | summarizer (adds `summary`) | `agents.py`, function returns the Story |
| **Generate a side artifact** | commentator (returns Comment) | `agents.py`, function returns a Comment-like dict |
| **Reduce many stories to one output** | curator, editor | `agents.py`, takes list, returns list or string |

## Steps

1. **Draft the prompt** at the top of `newsaggro/agents.py` as a module-level constant (e.g. `FACT_CHECKER_PROMPT = "..."`). Use `.format()` placeholders for the dynamic bits.
2. **Write the function.** Stateless. Takes input + `client`. Returns whatever the new agent produces.
3. **Wire it into `pipeline.py`** in the right slot. Parallel work goes inside a `ThreadPoolExecutor` block.
4. **Run end-to-end** (`python brief.py`) and inspect the output before iterating.
5. **Iterate on the prompt** with `/tune-prompt` once the wiring works.

## Adding a new commentator persona

This is the simplest case. To add a "Regulator" persona:

1. Add `"Regulator"` to `PERSONAS` in `config.py`.
2. Add a `"Regulator": "..."` entry to `COMMENTATOR_PROMPTS` in `agents.py`.
3. Done. The pipeline picks it up automatically.

## Conventions

- Agents are stateless functions, not classes. Pass `client` in.
- One Claude call per agent. Loops (critic/refiner) belong in `pipeline.py`.
- Print one line per agent invocation in `pipeline.py` so the run is debuggable.
- If you need structured output, ask Claude for JSON and parse it (see `curator` for the pattern).
