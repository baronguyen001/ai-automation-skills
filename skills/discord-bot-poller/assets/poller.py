"""Poll one Discord channel for new messages and dispatch a handler.

Env-only config: DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID. This uses Discord's
REST messages endpoint rather than the Gateway, so it is best for low-volume
automation inboxes. It honors 429 retry_after values and reset-after pacing.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Iterable

API_BASE = "https://discord.com/api/v10"


class DiscordPollError(RuntimeError):
    """Raised for missing config or non-retryable Discord API failures."""


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise DiscordPollError(f"missing required env var: {name}")
    return value


def _request_json(path: str, params: dict[str, str] | None = None) -> tuple[Any, float]:
    query = f"?{urllib.parse.urlencode(params)}" if params else ""
    req = urllib.request.Request(
        f"{API_BASE}{path}{query}",
        headers={
            "Authorization": f"Bot {_env('DISCORD_BOT_TOKEN')}",
            "User-Agent": "ai-automation-skills-discord-poller",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            wait = float(resp.headers.get("X-RateLimit-Reset-After") or 0)
            return json.loads(body), wait
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 429:
            try:
                retry_after = float(json.loads(body).get("retry_after", 1))
            except Exception:
                retry_after = 1.0
            time.sleep(retry_after)
            return _request_json(path, params)
        raise DiscordPollError(f"Discord API error {exc.code}: {body[:200]}") from exc


def fetch_new_messages(
    *,
    channel_id: str | None = None,
    after_id: str | None = None,
    limit: int = 50,
) -> tuple[list[dict[str, Any]], float]:
    """Fetch messages after after_id, returned oldest-to-newest."""
    cid = channel_id or _env("DISCORD_CHANNEL_ID")
    params = {"limit": str(max(1, min(limit, 100)))}
    if after_id:
        params["after"] = after_id
    data, wait = _request_json(f"/channels/{cid}/messages", params)
    messages = sorted(data, key=lambda item: int(item["id"]))
    return messages, wait


def dispatch_messages(
    messages: Iterable[dict[str, Any]],
    handler: Callable[[dict[str, Any]], None],
    last_message_id: str | None = None,
) -> str | None:
    """Call handler for each message and return the newest processed id."""
    newest = last_message_id
    for message in messages:
        handler(message)
        newest = message["id"]
    return newest


def poll_forever(
    handler: Callable[[dict[str, Any]], None],
    *,
    channel_id: str | None = None,
    last_message_id: str | None = None,
    poll_seconds: float = 5.0,
) -> None:
    """Continuously poll the channel and dispatch each new message."""
    cursor = last_message_id
    while True:
        messages, reset_after = fetch_new_messages(channel_id=channel_id, after_id=cursor)
        cursor = dispatch_messages(messages, handler, cursor)
        time.sleep(max(poll_seconds, reset_after))


if __name__ == "__main__":
    def print_message(message: dict[str, Any]) -> None:
        author = message.get("author", {}).get("username", "user")
        print(f"[{message['id']}] {author}: {message.get('content', '')}")

    poll_forever(print_message)
