"""Reuse a long, stable system-prompt prefix across many Gemini calls.

When the same large instruction block (rules, schema, few-shot examples) is
sent on every request, caching it once turns those repeated input tokens into
a cheaper cached-token rate. This wraps Gemini context caching: create the
cache once, then point every generate call at the cached handle.

Requires `google-genai`. GEMINI_API_KEY comes from the environment.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class CachedPrefix:
    name: str   # server-side cache handle, reused on every call
    model: str


def create_cache(
    system_prompt: str,
    *,
    model: str = "gemini-2.5-flash",
    ttl_seconds: int = 3600,
) -> CachedPrefix:
    """Cache a system-prompt prefix once and return a reusable handle."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    cache = client.caches.create(
        model=model,
        config=types.CreateCachedContentConfig(
            system_instruction=system_prompt,
            ttl=f"{ttl_seconds}s",
        ),
    )
    return CachedPrefix(name=cache.name, model=model)


def generate_with_cache(prefix: CachedPrefix, user_text: str) -> str:
    """Run a generation that bills the cached prefix at the cheaper rate."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(
        model=prefix.model,
        contents=user_text,
        config=types.GenerateContentConfig(cached_content=prefix.name),
    )
    return (resp.text or "").strip()


if __name__ == "__main__":
    # A deliberately long, stable prefix is what makes caching worthwhile.
    SYSTEM = "You are a strict JSON extractor. " + ("Follow the rules exactly. " * 200)
    handle = create_cache(SYSTEM, ttl_seconds=1800)
    print(generate_with_cache(handle, "Extract the company from: Acme Corp raised $4M."))
