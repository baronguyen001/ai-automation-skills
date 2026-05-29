import html
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request


def escape_html(text: str) -> str:
    """Escape untrusted text before putting it into Telegram HTML messages."""
    return html.escape(text, quote=False)


def send_telegram(
    text: str,
    *,
    parse_mode: str = "HTML",
    button: tuple[str, str] | None = None,
    photo_url: str | None = None,
    retries: int = 3,
) -> bool:
    """Send a Telegram message. Token and chat id come from env, never code."""
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    method = "sendPhoto" if photo_url else "sendMessage"
    payload: dict[str, str] = {
        "chat_id": chat_id,
        "parse_mode": parse_mode,
        "disable_web_page_preview": "true",
    }

    if photo_url:
        payload["photo"] = photo_url
        payload["caption"] = text
    else:
        payload["text"] = text

    if button:
        label, url = button
        payload["reply_markup"] = json.dumps(
            {"inline_keyboard": [[{"text": label, "url": url}]]}
        )

    data = urllib.parse.urlencode(payload).encode()
    api = f"https://api.telegram.org/bot{token}/{method}"

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(api, data=data, timeout=15) as response:
                response.read()
            return True
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                retry_after = 2**attempt
                try:
                    body = json.loads(exc.read().decode("utf-8"))
                    retry_after = body.get("parameters", {}).get(
                        "retry_after", retry_after
                    )
                except Exception:
                    pass
                time.sleep(float(retry_after))
                continue
            return False
        except Exception:
            time.sleep(2**attempt)

    return False


if __name__ == "__main__":
    message = f"<b>Job done</b>\nProcessed {escape_html('42 items')}."
    send_telegram(message, button=("Open dashboard", "https://example.com/dash"))
