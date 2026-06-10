"""A hardened requests.Session: retry + backoff + status-forcelist + timeouts.

Bare requests.get/post have two production failure modes: a single transient
429/5xx kills the run, and a slow endpoint hangs forever because no timeout is
set. This builds a Session with a urllib3 Retry policy (exponential backoff,
429/5xx in the status-forcelist, Retry-After honored) mounted on an adapter,
and a TimeoutSession that injects a default (connect, read) timeout into every
request. BYO base URL - nothing here is target-specific.
"""
from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter

try:  # urllib3 v2 path
    from urllib3.util.retry import Retry
except ImportError:  # pragma: no cover - very old urllib3
    from requests.packages.urllib3.util.retry import Retry  # type: ignore

# (connect timeout, read timeout) in seconds. A slightly-over-3s connect timeout
# plays well with TCP retransmit timing; read timeout caps a slow response.
DEFAULT_TIMEOUT: tuple[float, float] = (3.05, 30.0)


class TimeoutSession(requests.Session):
    """A Session that applies a default timeout when a call omits one."""

    def __init__(self, timeout: float | tuple[float, float] = DEFAULT_TIMEOUT) -> None:
        super().__init__()
        self._timeout = timeout

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self._timeout)
        return super().request(method, url, **kwargs)


def make_session(
    *,
    total_retries: int = 4,
    backoff_factor: float = 0.5,
    timeout: float | tuple[float, float] = DEFAULT_TIMEOUT,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
    allowed_methods: tuple[str, ...] = ("GET", "HEAD", "OPTIONS", "PUT", "DELETE"),
) -> TimeoutSession:
    """Build a Session with a retry policy and a default per-request timeout."""
    retry = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(allowed_methods),
        respect_retry_after_header=True,  # let the server's Retry-After pace us
        raise_on_status=False,            # surface the final response, don't raise mid-retry
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    session = TimeoutSession(timeout=timeout)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


if __name__ == "__main__":
    # Self-test without network: verify the policy is wired the way we claim.
    s = make_session(total_retries=4, backoff_factor=0.5)
    adapter = s.get_adapter("https://example.com")
    retry = adapter.max_retries
    assert retry.total == 4
    assert 429 in retry.status_forcelist and 503 in retry.status_forcelist
    assert retry.backoff_factor == 0.5
    assert retry.respect_retry_after_header is True
    assert s._timeout == DEFAULT_TIMEOUT
    print("http-retry-session OK:", retry.total, "retries,", sorted(retry.status_forcelist))
