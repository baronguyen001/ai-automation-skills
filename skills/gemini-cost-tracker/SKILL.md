---
name: gemini-cost-tracker
description: "Wrap Gemini API calls to log token usage and USD cost per call, including input, output, cached, and thinking tokens, with per-model and per-session summaries. Use when the user asks to track gemini cost, inspect gemini token usage, or estimate repeated LLM call spend."
---

# Gemini Cost Tracker

Use this skill when repeated Gemini calls need transparent token and cost accounting. It records usage metadata after each call and prints a simple per-model session summary.

## When to invoke

- User says: "track gemini cost" / "gemini token usage" / "how much is this LLM call costing"
- Code in the conversation uses: `google-genai`, Gemini REST responses, or repeated model calls in a batch.

## When NOT to invoke

- The user only makes one or two ad hoc calls per day.
- The user needs provider billing reconciliation rather than a local estimate.

## Concrete example

User input:

```text
Wrap this three-call Gemini ranking job so I can see model cost by session.
```

Output:

```python
# Copy assets/cost_tracker.py into your project, then:
from cost_tracker import CostTracker

tracker = CostTracker()

# resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
tracker.record("gemini-2.5-flash", resp.usage_metadata)

print(tracker.summary())
```

Example printed output:

```text
Calls: 3 | Total: $0.001242
  gemini-2.5-flash-lite: $0.000180
  gemini-2.5-flash: $0.001062
```

## Pattern to apply

1. Keep a small pricing table in USD per 1M tokens and mark it "verify before trusting."
2. After each Gemini call, read `usage_metadata` from the SDK response or `usageMetadata` from REST.
3. Subtract cached tokens from billable input tokens.
4. Count output plus thinking tokens at the output-token price.
5. Append one row per call and print a per-model summary at the end.

Reference: `assets/cost_tracker.py`.

## Source

Distilled from production use across the author's automation projects. v0.1.0.
See also: [[gemini-structured-output]].
