---
name: gemini-vision-extract
description: "Extract typed JSON from an image with Gemini - pass a receipt, invoice, screenshot, or chart and get fields back validated against a Pydantic schema, not prose. Key from the environment only. Use for read a receipt, parse an invoice image, OCR into structured data, extract fields from a screenshot, or image to JSON with gemini."
version: "1.0.0"
---

# Gemini Vision Extract

Use this skill when you have an image and need structured fields out of it - line items off a receipt, totals off an invoice, values off a chart - rather than a paragraph of description. The Gemini call is constrained with `response_mime_type=application/json` plus a Pydantic `response_schema`, so the output parses into a typed object every time.

## When to invoke

- User says: "read this receipt", "parse the invoice image", "OCR into structured data", "extract fields from a screenshot".
- Code in the conversation feeds an image to an LLM and then regex-scrapes prose for values.

## When NOT to invoke

- The source is already machine-readable text/HTML/PDF-with-text - extract directly, no vision model needed.
- You need pixel-perfect OCR of dense documents at scale; a dedicated document-AI service may fit better.

## Concrete example

User input:

```text
Pull merchant, date, and total out of these receipt photos into JSON.
```

Output:

```python
from vision_extract import Receipt, extract   # GEMINI_API_KEY in the environment

data = extract("receipt.png", schema=Receipt)
print(data.model_dump_json(indent=2))
# {"merchant": "Corner Cafe", "date": "2026-06-06", "total": 4.5, "currency": "USD", "items": [...]}
```

## Pattern to apply

1. Define a Pydantic model with optional fields and pass it as `response_schema`; make absent fields nullable.
2. Set `response_mime_type=application/json` so the model returns parseable JSON, not commentary.
3. Read `GEMINI_API_KEY` from the environment; never inline it.
4. Prefer `resp.parsed` (already a validated instance); fall back to validating `resp.text` if the SDK returns none.
5. Pick the right model tier - Flash for cheap high-volume extraction, Pro when accuracy matters (see [[gemini-flash-budget]]).

Reference: `assets/vision_extract.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[gemini-structured-output]], [[gemini-flash-budget]], [[gemini-cost-tracker]].

→ Build the full runnable bot with Trawlkit.
