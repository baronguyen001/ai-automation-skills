---
name: playwright-pdf-snapshot
description: "Render any URL to a headless PDF or PNG snapshot with Playwright and no committed cookies. Use when the user asks to archive a page, capture a dashboard/report, make a PDF snapshot, or save a page screenshot for downstream review."
version: "1.0.0"
---

# Playwright PDF Snapshot

Use this skill when a script needs a browser-rendered artifact from a URL: a PDF report, a full-page PNG, or a dashboard capture. The helper runs Chromium headless through Playwright, accepts optional extra headers from the caller, and does not ship cookies or credentials.

## When to invoke

- User says: "save this page as PDF", "capture a PNG snapshot", "archive the dashboard", "render this report URL".
- The page needs browser rendering rather than a raw HTTP download.

## When NOT to invoke

- The URL is a static file that can be downloaded directly.
- The page requires a persisted login session; use [[playwright-login-session]] first and keep state files gitignored.

## Concrete example

User input:

```text
Render the public report URL to both a PDF and a PNG after the run finishes.
```

Output:

```python
# Copy assets/snapshot.py into your project, then:
from snapshot import snapshot

paths = snapshot("https://example.com/report", out_dir="artifacts", name="report")
print(paths)
```

Install Playwright in the target project with `pip install playwright` and `python -m playwright install chromium`. Do not commit cookies, storage state, or private headers.

## Pattern to apply

1. Use headless Chromium and wait for network idle or a specific selector before capturing.
2. Save both PDF and PNG only when the downstream workflow needs both.
3. Keep auth out of this helper; pass public URLs or combine with a local, gitignored Playwright state file.
4. Use stable filenames so artifact upload steps can find them.
5. Pair with object storage when snapshots need to survive the local run.

Reference: `assets/snapshot.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[playwright-login-session]], [[s3-uploader]], [[csv-report-writer]].

→ Build the full runnable bot with Trawlkit.
