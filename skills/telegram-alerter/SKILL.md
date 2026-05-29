---
name: telegram-alerter
description: "Send a Telegram message/alert from Python - bot token and chat id from env, HTML formatting, inline buttons, photo attach, retry on 429. Use when the user asks to send a telegram alert, notify telegram, telegram bot send, or wire a script to push notifications to Telegram."
---

# Telegram Alerter

Use this skill when a Python script needs to push a Telegram notification without hardcoding credentials. It provides a dependency-light pattern for message/photo dispatch, inline buttons, and rate-limit retry handling.

## When to invoke

- User says: "send a telegram alert" / "notify telegram" / "telegram bot send"
- Code in the conversation uses: Python scripts that need job completion, failure, or digest notifications.

## When NOT to invoke

- The user wants Slack, Discord, email, or webhooks instead of Telegram.
- The user wants a full bot conversation framework with commands, state, and long polling.

## Concrete example

User input:

```text
Add a Telegram alert when my nightly scraper finishes and link to the dashboard.
```

Output:

```python
# Copy assets/send_alert.py into your project, then:
from send_alert import send_telegram

ok = send_telegram(
    "Job done: processed 42 items in 18 minutes.",
    button=("Open dashboard", "https://example.com/dash"),
)
if not ok:
    print("Telegram delivery failed after retries")
```

The helper reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from the environment. User-provided text should be HTML-escaped before formatting.

## Pattern to apply

1. Keep bot token and chat id in environment variables only.
2. Build a `sendMessage` payload by default and switch to `sendPhoto` when a photo URL is provided.
3. Use Telegram HTML formatting, but escape untrusted content.
4. Add inline keyboard JSON when a button label and URL are supplied.
5. Retry transient failures and honor `retry_after` on HTTP 429.

Reference: `assets/send_alert.py`.

## Source

Distilled from production use across the author's automation projects. v0.1.0.
See also: [[pr-body-formatter]].
