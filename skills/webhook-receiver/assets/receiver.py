"""Minimal stdlib webhook receiver: verify an HMAC signature, queue the payload.

No web framework. Inbound POSTs are authenticated with an HMAC-SHA256 signature
(shared secret in WEBHOOK_SECRET) compared in constant time, then the raw body
is written to a queue directory as one JSON file per event. A separate worker
(your scheduled script) drains the queue, so a slow handler never blocks or
drops a delivery. Nothing here trusts the network: bad signatures get 401.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

QUEUE_DIR = Path(os.environ.get("WEBHOOK_QUEUE", "webhook_queue"))
SECRET = os.environ.get("WEBHOOK_SECRET", "").encode()
SIG_HEADER = "X-Signature-256"  # value looks like "sha256=<hexdigest>"
MAX_BODY = 1 << 20  # 1 MiB cap; reject larger bodies to avoid memory abuse


def verify(body: bytes, signature: str) -> bool:
    """Constant-time compare of the request HMAC against our shared secret."""
    if not SECRET or not signature:
        return False
    expected = "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def enqueue(body: bytes) -> Path:
    """Write the raw payload to the queue as one timestamped JSON file."""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    path = QUEUE_DIR / f"{time.time_ns()}.json"
    path.write_bytes(body)
    return path


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 - stdlib dispatch name
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > MAX_BODY:
            self.send_response(413)
            self.end_headers()
            return
        body = self.rfile.read(length)
        if not verify(body, self.headers.get(SIG_HEADER, "")):
            self.send_response(401)
            self.end_headers()
            return
        try:
            json.loads(body)  # reject non-JSON early
        except ValueError:
            self.send_response(400)
            self.end_headers()
            return
        enqueue(body)
        self.send_response(202)  # accepted; the worker processes it later
        self.end_headers()

    def log_message(self, *_: object) -> None:
        pass  # silence default stderr logging; wire your own if needed


def serve(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"webhook receiver listening on {host}:{port}, queue -> {QUEUE_DIR}")
    server.serve_forever()


if __name__ == "__main__":
    serve()
