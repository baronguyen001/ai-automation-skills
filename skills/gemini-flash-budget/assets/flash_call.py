"""High-volume, low-cost Gemini extraction with thinking disabled.

For bulk classification or single-field extraction you usually do not want the
model to "think" - it adds latency and thinking-token cost for no quality gain
on simple, well-scoped prompts. Setting thinking_budget=0 on a Flash model
gives the cheapest, fastest path.

Requires `google-genai`. GEMINI_API_KEY comes from the environment.
"""
from __future__ import annotations

import os
from collections.abc import Iterable


def flash_extract(prompt: str, *, model: str = "gemini-2.5-flash") -> str:
    """One cheap, no-thinking Flash call. Returns stripped text."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return (resp.text or "").strip()


def flash_extract_many(prompts: Iterable[str], *, model: str = "gemini-2.5-flash") -> list[str]:
    """Map the cheap extractor over many inputs; failures degrade to ''."""
    out: list[str] = []
    for prompt in prompts:
        try:
            out.append(flash_extract(prompt, model=model))
        except Exception:
            out.append("")  # one bad row never kills the batch
    return out


if __name__ == "__main__":
    rows = [
        "Ticker for Apple Inc.?",
        "Ticker for Microsoft Corporation?",
    ]
    for prompt, answer in zip(rows, flash_extract_many(rows)):
        print(f"{prompt} -> {answer}")
