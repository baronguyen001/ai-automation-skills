---
name: gemini-prompt-cache
description: "Cache a long, stable Gemini system-prompt prefix once and reuse the handle across many calls so repeated instruction tokens bill at the cheaper cached rate instead of full input. Use for cache gemini system prompt, context caching, cut gemini input cost, cachedContent, or reuse a long prompt prefix."
version: "1.0.0"
---

# Gemini Prompt Cache

Use this skill when the same large instruction block - rules, a response schema, few-shot examples - is sent on every Gemini request. Caching that prefix once turns those repeated input tokens into a much cheaper cached-token rate, which matters a lot at volume. This wraps Gemini context caching: create the cache once, then point every generate call at the cached handle.

## When to invoke

- User says: "cache my gemini system prompt" / "cut gemini input cost" / "context caching" / "reuse a long prompt prefix"
- Code in the conversation uses: a fixed multi-thousand-token system instruction repeated across many `generate_content` calls.

## When NOT to invoke

- The system prompt is short, or it changes on every call (caching a one-off prefix loses money on the cache write).
- The user wants output-side savings (use [[gemini-flash-budget]] to drop thinking tokens instead).

## Concrete example

User input:

```text
I send the same 4k-token extraction ruleset to Gemini on every row. Stop paying full price for it.
```

Output:

```python
# Copy assets/cache.py into your project, then:
from cache import create_cache, generate_with_cache

prefix = create_cache(BIG_RULESET, model="gemini-2.5-flash", ttl_seconds=1800)
for row in rows:
    print(generate_with_cache(prefix, row))   # ruleset billed at cached rate
```

The helper reads `GEMINI_API_KEY` from the environment and requires `google-genai`.

## Pattern to apply

1. Separate the stable prefix (rules, schema, examples) from the per-call user text.
2. Create the cache once with `caches.create`, storing the returned handle and a TTL.
3. On each call, pass `cached_content=<handle>` so only the user text is billed at full input rate.
4. Match the TTL to your batch duration; a too-short TTL forces re-creation, a too-long one wastes storage.
5. Track the savings with [[gemini-cost-tracker]] to confirm the cache is paying off.

Reference: `assets/cache.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[gemini-flash-budget]], [[gemini-cost-tracker]].

→ Build the full runnable bot with Trawlkit.
