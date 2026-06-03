"""Fetch recent email over IMAP and build a daily digest.

Credentials come from the environment (IMAP_HOST, IMAP_USER,
IMAP_APP_PASSWORD) - use a provider app-password, never your login password.
ALLOWED_SENDERS below is a generic example of newsletter-style sources;
replace it with the domains you actually want in the digest.
"""
from __future__ import annotations

import email
import email.utils
import imaplib
import os
from datetime import datetime, timedelta, timezone
from email.header import decode_header


# Generic example allowlist. Swap for your own trusted sender domains.
ALLOWED_SENDERS = {
    "newsletter.example.com",
    "digest.example.org",
    "updates.example.net",
}


def _decode(value: str) -> str:
    """Decode a possibly MIME-encoded header into plain text."""
    out = []
    for text, enc in decode_header(value):
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def fetch_digest(since_hours: int = 24, allow: set[str] | None = None) -> list[dict[str, str]]:
    """Return allowlisted messages newer than `since_hours` as digest rows."""
    allow = allow or ALLOWED_SENDERS
    host = os.environ["IMAP_HOST"]
    user = os.environ["IMAP_USER"]
    password = os.environ["IMAP_APP_PASSWORD"]

    since = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).strftime("%d-%b-%Y")
    rows: list[dict[str, str]] = []

    with imaplib.IMAP4_SSL(host) as imap:
        imap.login(user, password)
        imap.select("INBOX", readonly=True)  # read-only: never marks mail as read
        status, data = imap.search(None, "SINCE", since)
        if status != "OK":
            return rows

        for num in data[0].split():
            status, raw = imap.fetch(num, "(RFC822)")
            if status != "OK" or not raw or not raw[0]:
                continue
            msg = email.message_from_bytes(raw[0][1])
            sender = email.utils.parseaddr(msg.get("From", ""))[1]
            domain = sender.rsplit("@", 1)[-1].lower()
            if not any(domain == d or domain.endswith("." + d) for d in allow):
                continue
            rows.append({
                "from": sender,
                "subject": _decode(msg.get("Subject", "(no subject)")),
                "date": msg.get("Date", ""),
            })

    return rows


def render_digest(rows: list[dict[str, str]]) -> str:
    """Render digest rows as one line per item."""
    if not rows:
        return "Daily digest: nothing new from allowlisted sources."
    lines = [f"Daily digest - {len(rows)} item(s):"]
    lines += [f"  - {r['subject']}  ({r['from']})" for r in rows]
    return "\n".join(lines)


if __name__ == "__main__":
    print(render_digest(fetch_digest(since_hours=24)))
