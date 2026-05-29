from dataclasses import dataclass, field
from typing import Any


# Prices are USD per 1M tokens. Verify against the current provider pricing
# page before using this estimate for budget decisions.
PRICING = {
    "gemini-2.5-flash-lite": {"in": 0.10, "out": 0.40, "cached": 0.025},
    "gemini-2.5-flash": {"in": 0.30, "out": 2.50, "cached": 0.075},
    "gemini-2.5-pro": {"in": 1.25, "out": 10.0, "cached": 0.31},
}


def _get_usage_value(usage: Any, snake_name: str, camel_name: str) -> int:
    if isinstance(usage, dict):
        return int(usage.get(snake_name) or usage.get(camel_name) or 0)
    return int(getattr(usage, snake_name, 0) or getattr(usage, camel_name, 0) or 0)


@dataclass
class CostTracker:
    rows: list[dict[str, float | int | str]] = field(default_factory=list)

    def record(self, model: str, usage: Any) -> dict[str, float | int | str]:
        prices = PRICING.get(model, PRICING["gemini-2.5-flash"])

        prompt_tokens = _get_usage_value(usage, "prompt_token_count", "promptTokenCount")
        output_tokens = _get_usage_value(
            usage, "candidates_token_count", "candidatesTokenCount"
        )
        cached_tokens = _get_usage_value(
            usage, "cached_content_token_count", "cachedContentTokenCount"
        )
        thinking_tokens = _get_usage_value(
            usage, "thoughts_token_count", "thoughtsTokenCount"
        )

        billable_input = max(prompt_tokens - cached_tokens, 0)
        usd = (
            billable_input * prices["in"]
            + cached_tokens * prices["cached"]
            + (output_tokens + thinking_tokens) * prices["out"]
        ) / 1_000_000

        row: dict[str, float | int | str] = {
            "model": model,
            "in": prompt_tokens,
            "cached": cached_tokens,
            "out": output_tokens,
            "think": thinking_tokens,
            "usd": usd,
        }
        self.rows.append(row)
        return row

    def summary(self) -> str:
        total = sum(float(row["usd"]) for row in self.rows)
        by_model: dict[str, float] = {}

        for row in self.rows:
            model = str(row["model"])
            by_model[model] = by_model.get(model, 0.0) + float(row["usd"])

        lines = [f"  {model}: ${cost:.6f}" for model, cost in by_model.items()]
        return f"Calls: {len(self.rows)} | Total: ${total:.6f}\n" + "\n".join(lines)
