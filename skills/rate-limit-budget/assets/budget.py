"""A token-bucket pacer with a hard per-run budget - generic, stdlib only.

Two problems when a run hammers an API: bursts earn 429s, and a runaway loop can
drain a free-tier monthly quota before you notice. This combines both controls.
A token bucket refills at rate_per_sec up to a burst capacity; acquire() blocks
just long enough to stay under the rate. A separate budget counter (max_calls,
or max_cost with a per-call weight) raises BudgetExceeded once the run hits its
cap, so you can stop cleanly. In-process only; for a cross-machine limiter use a
Redis token bucket. For a production library bound to a real provider, see the
baronguyen001/helius-rate-limiter repo cross-linked from the SKILL.
"""
from __future__ import annotations

import threading
import time


class BudgetExceeded(RuntimeError):
    """Raised by acquire() once the per-run call/cost budget is spent."""


class RateBudget:
    """Token-bucket rate limiter with an optional hard per-run budget."""

    def __init__(
        self,
        *,
        rate_per_sec: float,
        burst: float | None = None,
        max_calls: int | None = None,
        max_cost: float | None = None,
        _clock=time.monotonic,
        _sleep=time.sleep,
    ) -> None:
        if rate_per_sec <= 0:
            raise ValueError("rate_per_sec must be > 0")
        self.rate = float(rate_per_sec)
        self.capacity = float(burst if burst is not None else rate_per_sec)
        self.max_calls = max_calls
        self.max_cost = max_cost

        self._tokens = self.capacity
        self._updated = _clock()
        self._calls = 0
        self._cost = 0.0
        self._lock = threading.Lock()
        self._clock = _clock
        self._sleep = _sleep

    def _refill(self) -> None:
        now = self._clock()
        elapsed = now - self._updated
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            self._updated = now

    def acquire(self, cost: float = 1.0) -> None:
        """Block until a token is available; raise BudgetExceeded past the cap."""
        with self._lock:
            if self.max_calls is not None and self._calls >= self.max_calls:
                raise BudgetExceeded(f"per-run call budget reached: {self.max_calls}")
            if self.max_cost is not None and self._cost + cost > self.max_cost:
                raise BudgetExceeded(f"per-run cost budget reached: {self.max_cost}")

            self._refill()
            if self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self.rate
                self._sleep(wait)
                self._refill()
            self._tokens -= 1.0
            self._calls += 1
            self._cost += cost

    def stats(self) -> dict[str, float | int | None]:
        remaining = None if self.max_calls is None else self.max_calls - self._calls
        return {
            "calls": self._calls,
            "cost": round(self._cost, 6),
            "remaining": remaining,
            "tokens": round(self._tokens, 3),
        }


if __name__ == "__main__":
    # Self-test with a fake clock so it runs instantly and deterministically.
    fake = {"t": 0.0}
    slept = {"total": 0.0}

    def clock() -> float:
        return fake["t"]

    def sleep(secs: float) -> None:
        slept["total"] += secs
        fake["t"] += secs  # advance virtual time as if we slept

    pacer = RateBudget(
        rate_per_sec=5, burst=2, max_calls=3, _clock=clock, _sleep=sleep
    )
    # 2 burst tokens -> first two acquire with no sleep.
    pacer.acquire()
    pacer.acquire()
    assert slept["total"] == 0.0
    # Third drains the bucket and must wait ~1/5s for a refill.
    pacer.acquire()
    assert slept["total"] > 0.0
    # Fourth exceeds max_calls=3.
    try:
        pacer.acquire()
        raise AssertionError("expected BudgetExceeded")
    except BudgetExceeded:
        pass

    s = pacer.stats()
    assert s["calls"] == 3 and s["remaining"] == 0
    print("rate-limit-budget OK:", s, "slept", round(slept["total"], 3), "s")
