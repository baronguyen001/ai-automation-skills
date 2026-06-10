---
name: http-retry-session
description: "A hardened requests.Session with urllib3 Retry - exponential backoff, a status-forcelist for 429/5xx, honored Retry-After, and a hard connect/read timeout on every call. Use when the user asks to make HTTP calls more reliable, add retries to requests, handle 429 rate limits, set request timeouts, or stop a scraper from hanging on a slow endpoint."
version: "1.0.0"
---

# HTTP Retry Session

Use this skill when a script makes outbound HTTP calls and a single transient failure (a 429, a 503, a dropped connection) should not crash the run - and a slow endpoint should never hang it forever. It wires a `requests.Session` with a `urllib3` `Retry` policy (backoff + status-forcelist + honored `Retry-After`) and a `TimeoutSession` subclass that applies a default connect/read timeout to every request unless overridden.

## When to invoke

- User says: "add retries to my requests", "handle 429s", "set a timeout on these calls", "the scraper hangs on a slow URL".
- Code in the conversation calls `requests.get`/`post` bare, with no retry policy and no timeout.

## When NOT to invoke

- A single fire-and-forget call where a failure should fail loudly and immediately.
- You need full async concurrency - reach for `httpx`/`aiohttp` with their own retry/timeout setup instead.

## Concrete example

User input:

```text
My API client randomly dies on 429s and once hung for ten minutes. Make it resilient.
```

Output:

```python
# Copy assets/session.py into your project, then:
from session import make_session

# BYO base URL via env or config; nothing target-specific is hardcoded.
session = make_session(total_retries=4, backoff_factor=0.5, timeout=(3.05, 30))

resp = session.get("https://api.example.com/v1/items", params={"page": 1})
resp.raise_for_status()        # retries already exhausted 429/5xx by here
data = resp.json()
```

Every call now retries idempotent methods on 429/500/502/503/504 with exponential backoff (and respects a `Retry-After` header), and applies a `(connect, read)` timeout so no request hangs indefinitely.

## Pattern to apply

1. Mount one `HTTPAdapter` with a `Retry` on both `http://` and `https://`; reuse the session for connection pooling.
2. Put 429 and 5xx in `status_forcelist`; set `respect_retry_after_header=True` so the server's pacing wins.
3. Set `backoff_factor` so waits grow exponentially (0.5 -> ~0.5s, 1s, 2s, 4s); cap `total` retries.
4. Apply a default `(connect, read)` timeout to every request - never call without one, that is what hangs.
5. Keep retries to idempotent methods (`allowed_methods`); do not silently retry a non-idempotent POST.

Reference: `assets/session.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[proxy-rotator]], [[rate-limit-budget]], [[webhook-receiver]].

→ Build the full runnable bot with Trawlkit.
