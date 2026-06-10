"""Post a run result to a Slack incoming webhook, Block Kit + colored attachment.

An incoming webhook is the lightest way to push a status into Slack: no bot
token, no SDK, just one POST of a JSON payload. This builds a header/section
Block Kit message wrapped in an attachment whose color encodes the run status
(green ok / red error / yellow warn) and posts it with stdlib urllib, retrying
transient failures. The webhook URL is a secret and is read from the env only.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

_COLORS = {"ok": "#2eb67d", "error": "#e01e5a", "warn": "#ecb22e"}


def build_payload(
    title: str,
    text: str,
    *,
    status: str = "ok",
    fields: dict[str, str] | None = None,
    link: tuple[str, str] | None = None,
) -> dict:
    """Build a Slack Block Kit payload wrapped in a colored attachment."""
    blocks: list[dict] = [
        {"type": "header", "text": {"type": "plain_text", "text": title[:150]}},
        {"type": "section", "text": {"type": "mrkdwn", "text": text}},
    ]
    if fields:
        blocks.append(
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*{k}*\n{v}"} for k, v in fields.items()
                ],
            }
        )
    if link:
        label, url = link
        blocks.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": label},
                        "url": url,
                    }
                ],
            }
        )
    return {
        "attachments": [
            {"color": _COLORS.get(status, _COLORS["ok"]), "blocks": blocks}
        ]
    }


def send_slack(
    title: str,
    text: str,
    *,
    status: str = "ok",
    fields: dict[str, str] | None = None,
    link: tuple[str, str] | None = None,
    retries: int = 3,
) -> bool:
    """Post to the Slack incoming webhook in SLACK_WEBHOOK_URL. Returns success."""
    url = os.environ["SLACK_WEBHOOK_URL"]
    payload = build_payload(
        title, text, status=status, fields=fields, link=link
    )
    data = json.dumps(payload).encode("utf-8")

    for attempt in range(retries):
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                response.read()
            return True
        except urllib.error.HTTPError as exc:
            # 429 (rate limited) and 5xx are worth a retry; 4xx config errors are not.
            if exc.code == 429 or 500 <= exc.code < 600:
                time.sleep(2**attempt)
                continue
            return False
        except Exception:
            time.sleep(2**attempt)

    return False


if __name__ == "__main__":
    # Self-test without network: build a payload and print it.
    sample = build_payload(
        "Nightly scrape finished",
        "Processed 42 items in 18 minutes.",
        status="ok",
        fields={"Items": "42", "Duration": "18m"},
        link=("Open dashboard", "https://example.com/dash"),
    )
    assert sample["attachments"][0]["color"] == "#2eb67d"
    assert sample["attachments"][0]["blocks"][0]["type"] == "header"
    print(json.dumps(sample, indent=2))
