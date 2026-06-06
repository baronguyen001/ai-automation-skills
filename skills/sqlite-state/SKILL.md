---
name: sqlite-state
description: "Give scheduled scripts memory between runs with one SQLite file - a seen-set for dedup, a key/value cursor to resume where you left off, and order-preserving new-item filtering. Use for dedup across runs, don't re-alert the same item, remember the last id, resume a scraper, or persist state between cron runs."
version: "1.0.0"
---

# SQLite State

Use this skill when a recurring job must remember what it already did - which items it has alerted on, the last cursor it processed - so it does not re-notify or re-scrape on the next tick. One stdlib SQLite file gives durable, file-locked state with no server and no extra dependency.

## When to invoke

- User says: "don't alert the same thing twice", "dedup across runs", "remember the last id", "resume where it left off".
- Code in the conversation is a cron/scheduled script that currently re-processes everything each run.

## When NOT to invoke

- State is tiny and ephemeral within a single run - a plain set/dict is enough.
- Multiple machines must share state concurrently; reach for a real server DB instead of a single file.

## Concrete example

User input:

```text
My news scraper re-sends the same headlines every hour. Make it only send new ones.
```

Output:

```python
from state import filter_new, mark_seen

db = "news.db"
fresh = filter_new(db, [a["url"] for a in articles])   # only unseen URLs
for url in fresh:
    send_alert(url)
mark_seen(db, *fresh)                                   # remember them for next run
```

## Pattern to apply

1. Key each item by something stable and unique (URL, id, content hash), not by array position.
2. Use `filter_new` to decide what to act on, then `mark_seen` only after the action succeeds.
3. Store progress as a named cursor (`set_cursor`/`get_cursor`) so a resumable scraper restarts mid-stream.
4. Enable WAL mode for durable writes with concurrent readers; keep a single writer.
5. Back up or version the one `.db` file - it is the whole memory of the job.

Reference: `assets/state.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[pipeline-orchestrator]], [[cron-dispatch]], [[webhook-receiver]].

→ Build the full runnable bot with Trawlkit.
