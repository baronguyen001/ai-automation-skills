---
name: s3-uploader
description: "Upload and download run artifacts from S3-compatible storage with BYO bucket and credentials from env. Use when the user asks to store scraper output, archive reports, publish artifacts to object storage, fetch a prior run file, or use MinIO/R2/Spaces/S3 without hardcoding credentials."
version: "1.0.0"
---

# S3 Uploader

Use this skill when an automation run needs durable artifact storage: CSV reports, PDFs, JSON checkpoints, screenshots, model outputs, or logs that should survive outside the local machine. The helper targets generic S3-compatible storage and reads bucket, endpoint, and credentials from environment variables only.

## When to invoke

- User says: "upload this report to S3", "save artifacts to object storage", "download the last run file", "use MinIO/R2/Spaces".
- Code in the conversation writes files locally but needs a portable handoff or archive location.

## When NOT to invoke

- The artifact is only needed inside the same process; keep it on disk.
- The user needs a public website CDN workflow with cache invalidation and signed URLs.

## Concrete example

User input:

```text
Upload the generated CSV to my S3-compatible bucket after the scraper finishes.
```

Output:

```python
# Copy assets/s3.py into your project, then:
from s3 import upload_file

key = upload_file("out/daily_report.csv", key="reports/daily_report.csv")
print("uploaded:", key)
```

The helper reads `S3_BUCKET`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, optional `S3_ENDPOINT_URL`, and optional `S3_REGION` from the environment. Nothing target-specific or secret is committed.

## Pattern to apply

1. Keep bucket name, endpoint, access key, and secret key in env vars only.
2. Use deterministic object keys such as `reports/YYYY-MM-DD/name.csv` so reruns are easy to find.
3. Upload only after the local file is complete; never stream a half-written artifact.
4. Support S3-compatible endpoints by passing `endpoint_url` instead of hardcoding AWS.
5. Fail with a clear config error when env vars or client libraries are missing.

Reference: `assets/s3.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[csv-report-writer]], [[playwright-pdf-snapshot]], [[pipeline-orchestrator]].

→ Build the full runnable bot with Trawlkit.
