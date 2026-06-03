---
name: gemini-flash-budget
description: "Run high-volume, low-cost Gemini extraction on a Flash model with thinking_budget=0 so simple, well-scoped prompts skip thinking tokens entirely - cheapest and fastest path for bulk classification and field extraction. Use for cheap gemini extraction, disable gemini thinking, thinking_budget 0, bulk classify with flash, or high volume gemini calls."
version: "1.0.0"
---

# Gemini Flash Budget

Use this skill when you need to run a model over many rows for a simple, well-scoped task - extract a ticker, classify a sentence, pull one field. On those prompts the model's "thinking" adds latency and thinking-token cost for no quality gain. Setting `thinking_budget=0` on a Flash model gives the cheapest, fastest path; the savings compound across thousands of calls.

## When to invoke

- User says: "make these gemini calls cheaper" / "disable thinking" / "bulk classify with flash" / "high-volume extraction"
- Code in the conversation uses: a loop of many small Gemini calls for extraction or classification.

## When NOT to invoke

- The task needs multi-step reasoning, where thinking actually improves accuracy (keep a thinking budget then).
- The cost is on the input side from a repeated prefix (use [[gemini-prompt-cache]] instead).

## Concrete example

User input:

```text
I run 5,000 Gemini calls a day just to map company names to tickers. Cut the cost.
```

Output:

```python
# Copy assets/flash_call.py into your project, then:
from flash_call import flash_extract_many

prompts = [f"Ticker for: {name}?" for name in company_names]
tickers = flash_extract_many(prompts)   # Flash, temperature 0, no thinking tokens
```

The helper reads `GEMINI_API_KEY` from the environment and requires `google-genai`.

## Pattern to apply

1. Confirm the task is simple and well-scoped - the kind where reasoning adds nothing.
2. Pick a Flash model and set `temperature=0.0` for determinism.
3. Set `thinking_config=ThinkingConfig(thinking_budget=0)` to skip thinking tokens.
4. Map the call over the batch; degrade individual failures to empty strings so one bad row never kills the run.
5. Verify quality on a sample before scaling, and log spend with [[gemini-cost-tracker]].

Reference: `assets/flash_call.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[gemini-prompt-cache]], [[gemini-cost-tracker]].

→ Build the full runnable bot with Trawlkit.
