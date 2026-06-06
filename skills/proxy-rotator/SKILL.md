---
name: proxy-rotator
description: "Rotate a pool of HTTP/SOCKS proxies with round-robin selection, failure tracking, and a cooldown that benches dead proxies before retrying. BYO proxy list via env - none are shipped. Use for rotate proxies, spread requests across proxies, avoid IP bans, retry through a different proxy, or proxy health check."
version: "1.0.0"
---

# Proxy Rotator

Use this skill when a scraper must spread requests across several proxies and stop hammering ones that have gone dead. The rotator hands out the next healthy proxy, counts failures, and benches a proxy for a cooldown window after it fails too often - then gives it another chance. You bring the proxy list; nothing is committed.

## When to invoke

- User says: "rotate proxies", "spread requests across proxies", "stop getting IP-banned", "retry through another proxy".
- Code in the conversation makes many outbound requests and needs to distribute them across a proxy pool.

## When NOT to invoke

- A single connection is fine, or the target explicitly permits your volume - rotating proxies adds needless complexity.
- The intent is to evade an explicit block or abuse a service; keep usage within the target's terms.

## Concrete example

User input:

```text
I have 5 proxies. Round-robin them and skip any that start failing.
```

Output:

```python
import requests
from rotator import ProxyRotator

rot = ProxyRotator.from_env()        # PROXY_POOL="http://h1:8080,socks5://h2:1080,..."
for url in urls:
    p = rot.get()                    # next healthy proxy
    try:
        r = requests.get(url, proxies=p.as_dict(), timeout=15)
        rot.report(p, ok=r.ok)       # feed the result back so the pool self-heals
    except Exception:
        rot.report(p, ok=False)      # too many fails -> benched for the cooldown
```

## Pattern to apply

1. Load proxies from the environment or a gitignored file - never commit real proxy URLs or credentials.
2. Always call `report(proxy, ok=...)` after each request so failing proxies get benched automatically.
3. Tune `max_fails` and `cooldown` to the target; a short cooldown recovers flaky proxies, a long one drops bad ones.
4. Run `health_check` before a big batch to bench dead proxies up front.
5. Handle the "no healthy proxies" error - back off and retry rather than crashing the run.

Reference: `assets/rotator.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[playwright-login-session]], [[pipeline-orchestrator]], [[cron-dispatch]].

→ Build the full runnable bot with Trawlkit.
