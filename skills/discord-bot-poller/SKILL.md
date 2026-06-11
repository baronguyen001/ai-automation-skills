---
name: discord-bot-poller
description: "Poll a Discord channel for new messages with a bot token from env and dispatch a handler while honoring REST rate limits. Use when the user asks to watch a Discord channel, trigger automation from Discord messages, or build a lightweight Discord inbox without committing tokens."
version: "1.0.0"
---

# Discord Bot Poller

Use this skill when an automation job needs to watch one Discord channel and react to new messages without a full gateway bot framework. The helper uses the Discord REST API, stores the last seen message id in memory or a caller-provided value, and honors rate-limit responses.

## When to invoke

- User says: "poll a Discord channel", "trigger this from Discord", "watch messages and run a handler".
- The workflow needs a small single-channel inbox, not slash commands or real-time presence.

## When NOT to invoke

- The user needs a full interactive bot; use `discord.py` and the Gateway instead.
- The bot must receive messages instantly at high volume across many channels.

## Concrete example

User input:

```text
Poll my Discord alerts channel and send each new URL into the scraper.
```

Output:

```python
# Copy assets/poller.py into your project, then:
from poller import poll_forever

def handle(message):
    print(message["author"].get("username", "user"), message.get("content", ""))

poll_forever(handle, poll_seconds=5)
```

The helper reads `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` from env. Keep channel ids and tokens out of source control; persist `last_message_id` with [[sqlite-state]] if the poller must resume after restarts.

## Pattern to apply

1. Use a bot token from env and grant the bot access only to the channel it needs.
2. Poll `GET /channels/{channel_id}/messages` with `after=last_message_id` to avoid reprocessing.
3. Dispatch oldest-to-newest so handlers see messages in natural order.
4. Honor HTTP 429 `retry_after` and `X-RateLimit-Reset-After` before the next request.
5. Persist the last processed message id only after the handler succeeds.

Reference: `assets/poller.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[sqlite-state]], [[telegram-alerter]], [[rate-limit-budget]].

→ Build the full runnable bot with Trawlkit.
