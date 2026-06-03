---
name: gmail-imap-digest
description: "Pull recent email over IMAP, keep only messages from an allowlist of trusted sender domains, and render a daily digest - credentials from env using a provider app-password, never a login password. Use for email digest, fetch newsletters by IMAP, summarize inbox daily, gmail app password fetch, or build a morning email roundup."
version: "1.0.0"
---

# Gmail IMAP Digest

Use this skill when a user wants a daily roundup of newsletter-style email pulled over IMAP, filtered to sources they actually trust. It reads inbox messages since a cutoff, keeps only allowlisted sender domains, and renders a compact digest you can pipe straight into an alert. Works with any IMAP provider; Gmail just needs an app-password with IMAP enabled.

## When to invoke

- User says: "build a daily email digest" / "fetch my newsletters" / "summarize my inbox each morning" / "IMAP fetch"
- Code in the conversation uses: scheduled inbox reads, sender filtering, or a morning roundup job.

## When NOT to invoke

- The user wants to send mail (SMTP), not read it.
- The integration should use a provider's OAuth API (Gmail API) rather than plain IMAP.

## Concrete example

User input:

```text
Every morning, pull anything new from my three AI newsletters and give me a one-line-per-item digest.
```

Output:

```python
# Copy assets/imap_fetch.py into your project, then:
from imap_fetch import fetch_digest, render_digest

rows = fetch_digest(since_hours=24, allow={"newsletter.example.com", "digest.example.org"})
print(render_digest(rows))
# Daily digest - 2 item(s):
#   - Weekly model roundup  (news@newsletter.example.com)
#   - New tools this week    (hello@digest.example.org)
```

The helper reads `IMAP_HOST`, `IMAP_USER`, and `IMAP_APP_PASSWORD` from the environment. See `assets/.env.example` for the placeholder file.

## Pattern to apply

1. Connect over `IMAP4_SSL` and open the inbox read-only so nothing is marked read.
2. Search `SINCE` a date cutoff to bound the scan.
3. Parse each message's `From` address and keep only allowlisted domains (exact or subdomain match).
4. Decode MIME-encoded subjects before display.
5. Render a flat digest and hand it to an alert channel (see [[telegram-alerter]]).

Reference: `assets/imap_fetch.py`, `assets/.env.example`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[pipeline-orchestrator]], [[telegram-alerter]].

→ Build the full runnable bot with Trawlkit.
