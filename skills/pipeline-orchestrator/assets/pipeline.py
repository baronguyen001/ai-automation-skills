"""Generic scrape -> AI -> alert pipeline with retry and on-disk state.

Each stage is a plain callable: it takes the previous stage's output and
returns the next stage's input. State is checkpointed to a JSON file after
every stage, so a crashed or rate-limited run resumes from the last good step
instead of re-scraping from scratch. No credentials live here; each stage
reads its own environment.
"""
from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any


Stage = Callable[[Any], Any]


def run_stage(stage: Stage, value: Any, *, retries: int = 3, base_delay: float = 2.0) -> Any:
    """Run one stage with exponential-backoff retry on any exception."""
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            return stage(value)
        except Exception as exc:  # stages own their error types
            last_exc = exc
            time.sleep(base_delay * (2 ** attempt))
    name = getattr(stage, "__name__", repr(stage))
    raise RuntimeError(f"stage '{name}' failed after {retries} tries") from last_exc


def run_pipeline(
    stages: list[Stage],
    seed: Any = None,
    *,
    state_path: str | Path = ".pipeline_state.json",
    resume: bool = True,
) -> Any:
    """Run stages in order, checkpointing output after each one.

    On resume, already-completed stages are skipped and their cached output is
    reused. Delete the state file (or pass resume=False) to force a clean run.
    """
    path = Path(state_path)
    state: dict[str, Any] = {"done": -1, "value": seed}
    if resume and path.exists():
        state = json.loads(path.read_text(encoding="utf-8"))

    value = state["value"]
    for index, stage in enumerate(stages):
        if index <= state["done"]:
            continue  # already completed on a previous run
        value = run_stage(stage, value)
        state = {"done": index, "value": value}
        path.write_text(json.dumps(state, default=str), encoding="utf-8")

    return value


if __name__ == "__main__":
    def scrape(_: Any) -> list[dict[str, str]]:
        return [{"title": "Example item", "url": "https://example.com/1"}]

    def summarize(items: list[dict[str, str]]) -> str:
        return f"Found {len(items)} item(s): " + ", ".join(i["title"] for i in items)

    def alert(text: str) -> str:
        print(f"[alert] {text}")  # swap for telegram-alerter in production
        return text

    run_pipeline([scrape, summarize, alert], state_path=".pipeline_state.json", resume=False)
