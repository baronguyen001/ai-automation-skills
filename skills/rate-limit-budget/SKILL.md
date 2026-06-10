---
name: rate-limit-budget
description: "A token-bucket pacer that keeps API calls under a per-second rate AND a hard per-run budget - acquire() blocks just enough to smooth bursts, and a spend cap stops the run before it blows a free-tier quota. Generic and stdlib-only. Use when the user asks to rate-limit API calls, throttle requests, stay under a quota, cap calls per run, or avoid 429s by pacing instead of retrying."
version: "1.0.0"
---

# Rate Limit Budget

Use this skill when a run hammers an API and you want to pace it - smooth bursts to a steady rate so you stop earning 429s, and stop the whole run once a per-run call/credit budget is spent so a free-tier monthly quota survives. It is a token-bucket pacer: `acquire()` blocks just long enough to stay under the configured rate, and a separate budget counter raises once the run hits its cap. This is the teaching version; for the production library wired to a specific provider, see the cross-linked `helius-rate-limiter` repo.

## When to invoke

- User says: "rate-limit my API calls", "throttle these requests", "stay under the free-tier quota", "cap how many calls this run makes".
- Code in the conversation loops over many items and fires one API call each, with nothing pacing it.

## When NOT to invoke

- The server already paces you cleanly and a retry-on-429 (see `http-retry-session`) is enough.
- You need a distributed limiter shared across many machines - reach for Redis token buckets instead of an in-process one.

## Concrete example

User input:

```text
I call an API once per token and there are 400 of them. Keep it under 5 req/sec and never make more than 300 calls in one run.
```

Output:

```python
# Copy assets/budget.py into your project, then:
from budget import RateBudget, BudgetExceeded

pacer = RateBudget(rate_per_sec=5, burst=5, max_calls=300)

for token in tokens:
    try:
        pacer.acquire()              # blocks just enough to hold 5 req/sec
    except BudgetExceeded:
        print("hit the per-run call budget; stopping early")
        break
    call_api(token)

print(pacer.stats())                 # {"calls": 300, "remaining": 0, ...}
```

The pacer smooths bursts to the target rate and stops the run cleanly at the budget instead of discovering the quota is gone via a wall of 429s.

## Pattern to apply

1. Set `rate_per_sec` to the provider's documented limit (with headroom); `burst` is how many you may fire back-to-back.
2. Call `acquire()` immediately before each call - it sleeps only when you are ahead of schedule.
3. Set `max_calls` (or `max_cost` with a per-call weight) so a runaway loop cannot drain a monthly quota.
4. Catch `BudgetExceeded` and stop gracefully - log what is left to do so the next run resumes, do not crash.
5. Pair with `http-retry-session`: pacing prevents most 429s, retry handles the rare one that slips through.

For the production-hardened library tied to a real provider, see
[`baronguyen001/helius-rate-limiter`](https://github.com/baronguyen001/helius-rate-limiter).

Reference: `assets/budget.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[http-retry-session]], [[proxy-rotator]], [[gemini-flash-budget]].

→ Build the full runnable bot with Trawlkit.
