---
name: slack-webhook-alerter
description: "Post run results to a Slack incoming webhook from Python - webhook URL from env, Block Kit sections plus a colored attachment, no Slack SDK. Use when the user asks to send a slack alert, notify slack, post to a slack channel, mirror telegram alerts to slack, or wire a script to push a status message to Slack."
version: "1.0.0"
---

# Slack Webhook Alerter

Use this skill when a Python script needs to post a status or result to Slack and you do not want the full Slack SDK or a bot token - an incoming webhook is enough. It builds a Block Kit message with a colored attachment (green/red by status) and posts it with a stdlib request, retrying on transient failures. It mirrors `telegram-alerter` so the same run can fan out to both channels.

## When to invoke

- User says: "send a slack alert", "notify slack", "post to a slack channel", "mirror my telegram alerts to slack".
- Code in the conversation already pushes a run summary somewhere and should also reach a Slack channel.

## When NOT to invoke

- The user wants Telegram, Discord, or email instead - use the matching alerter.
- The user needs interactive Slack features (slash commands, modals, threads, reactions); a one-way incoming webhook cannot do those - reach for a bot token and the Slack API.

## Concrete example

User input:

```text
After my nightly job finishes, post a green or red Slack message with the item count and a dashboard link.
```

Output:

```python
# Copy assets/slack_alert.py into your project, then:
from slack_alert import send_slack

ok = send_slack(
    title="Nightly scrape finished",
    text="Processed 42 items in 18 minutes.",
    status="ok",                                  # ok -> green, error -> red, warn -> yellow
    fields={"Items": "42", "Duration": "18m"},
    link=("Open dashboard", "https://example.com/dash"),
)
if not ok:
    print("Slack delivery failed after retries")
```

The helper reads `SLACK_WEBHOOK_URL` from the environment. The webhook URL is itself a secret (it grants posting to that channel), so it is never hardcoded.

## Pattern to apply

1. Keep the incoming-webhook URL in `SLACK_WEBHOOK_URL` only - it is a secret, treat it like a token.
2. Map a status string to an attachment color so green/red is readable at a glance.
3. Build a `header` + `section` block for the title and body, and a fields list for key/value pairs.
4. Post the JSON payload with a short timeout and retry transient failures with exponential backoff.
5. Escape or trust the text you pass; Slack renders a limited mrkdwn subset, so keep user content plain.

Reference: `assets/slack_alert.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[telegram-alerter]], [[http-retry-session]], [[pipeline-orchestrator]].

→ Build the full runnable bot with Trawlkit.
