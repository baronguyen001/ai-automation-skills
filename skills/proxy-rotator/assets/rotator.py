"""Rotate a pool of HTTP/SOCKS proxies with health tracking and cooldown.

BYO proxy list (env or file) - none ship here. The rotator hands out the next
healthy proxy round-robin, marks a proxy unhealthy after repeated failures, and
benches it for a cooldown window before trying it again. An optional health
check pings a known URL through each proxy. Pure stdlib; the proxy dict it
returns plugs straight into requests/httpx (`proxies=`).
"""
from __future__ import annotations

import os
import time
import urllib.request
from dataclasses import dataclass, field


@dataclass
class Proxy:
    url: str  # "http://user:pass@host:port" or "socks5://host:port"
    fails: int = 0
    cooldown_until: float = 0.0

    def as_dict(self) -> dict[str, str]:
        return {"http": self.url, "https": self.url}


@dataclass
class ProxyRotator:
    proxies: list[Proxy]
    max_fails: int = 3  # mark unhealthy after this many consecutive fails
    cooldown: float = 300.0  # seconds benched before a retry
    _i: int = field(default=0, init=False)

    @classmethod
    def from_env(cls, var: str = "PROXY_POOL", **kw: object) -> "ProxyRotator":
        """Build from a comma/newline-separated env var of proxy URLs."""
        raw = os.environ.get(var, "")
        urls = [u.strip() for u in raw.replace("\n", ",").split(",") if u.strip()]
        return cls([Proxy(u) for u in urls], **kw)  # type: ignore[arg-type]

    def _available(self, now: float) -> list[Proxy]:
        return [p for p in self.proxies if p.cooldown_until <= now]

    def get(self) -> Proxy:
        """Return the next healthy proxy, round-robin. Raises if none available."""
        pool = self._available(time.time())
        if not pool:
            raise RuntimeError("no healthy proxies available (all in cooldown)")
        proxy = pool[self._i % len(pool)]
        self._i += 1
        return proxy

    def report(self, proxy: Proxy, ok: bool) -> None:
        """Feed back the result of a request so the pool self-heals."""
        if ok:
            proxy.fails = 0
            proxy.cooldown_until = 0.0
            return
        proxy.fails += 1
        if proxy.fails >= self.max_fails:
            proxy.cooldown_until = time.time() + self.cooldown
            proxy.fails = 0  # reset; it gets a fresh chance after the cooldown

    def health_check(self, test_url: str = "https://httpbin.org/ip", timeout: float = 10.0) -> None:
        """Probe every proxy once; bench the ones that fail."""
        for proxy in self.proxies:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxy.as_dict()))
            try:
                opener.open(test_url, timeout=timeout).read(1)
                self.report(proxy, ok=True)
            except Exception:
                self.report(proxy, ok=False)


if __name__ == "__main__":
    # BYO: export PROXY_POOL="http://host1:8080,socks5://host2:1080"
    rot = ProxyRotator.from_env()
    if not rot.proxies:
        print("set PROXY_POOL to a comma-separated list of proxy URLs")
    else:
        p = rot.get()
        print("use proxy:", p.as_dict())
        rot.report(p, ok=False)  # tell the rotator if the request failed
