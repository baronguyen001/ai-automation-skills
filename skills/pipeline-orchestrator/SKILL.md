---
name: pipeline-orchestrator
description: "Chain a scrape -> AI -> alert pipeline where each stage is a plain callable, with exponential-backoff retry per stage and a JSON state checkpoint between stages so a crashed or rate-limited run resumes instead of restarting. Use for chain pipeline steps, scrape then summarize then notify, retry between stages, resumable pipeline, or orchestrate a job."
version: "1.0.0"
---

# Pipeline Orchestrator

Use this skill when an automation job is really a chain of steps - scrape, then run it through an AI model, then send an alert - and you want each step to retry on transient failure and the whole run to resume from the last good step. It is a generic, dependency-light runner: stages are ordinary functions, and state is checkpointed to a JSON file so a 429 in the AI step never forces a full re-scrape.

## When to invoke

- User says: "chain these steps" / "scrape then summarize then notify" / "make the pipeline resumable" / "retry between stages"
- Code in the conversation uses: a script that does fetch -> transform -> deliver in sequence and fails partway through.

## When NOT to invoke

- The work is a single call with no real stages.
- The user needs a distributed DAG engine (Airflow, Temporal) with workers and a scheduler, not a single-process chain.

## Concrete example

User input:

```text
My nightly job scrapes a board, asks Gemini to summarize, then pushes Telegram. If Gemini rate-limits, don't re-scrape.
```

Output:

```python
# Copy assets/pipeline.py into your project, then:
from pipeline import run_pipeline

def scrape(_):     return fetch_board()          # your scraper
def summarize(rows): return gemini_summary(rows) # your AI step
def alert(text):   return send_telegram(text)    # see telegram-alerter

# checkpoints after each stage; a crash in summarize resumes there, not at scrape
result = run_pipeline([scrape, summarize, alert], state_path=".nightly_state.json")
```

## Pattern to apply

1. Model the job as an ordered list of single-argument callables; each returns the next stage's input.
2. Wrap every stage in exponential-backoff retry so a transient error does not kill the run.
3. Checkpoint `{done_index, value}` to a JSON file after each successful stage.
4. On resume, skip completed stages and reuse their cached output.
5. Keep credentials out of the runner - each stage reads its own env (see [[telegram-alerter]], [[gemini-flash-budget]]).

Reference: `assets/pipeline.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[cron-dispatch]], [[telegram-alerter]].

→ Build the full runnable bot with Trawlkit.
