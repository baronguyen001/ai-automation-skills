---
name: notion-row-writer
description: "Upsert a row into a Notion database by a stable key with NOTION_API_KEY and database id from env. Use when the user asks to write automation results to Notion, update a tracker row, dedupe by URL/id/date, or keep a lightweight Notion database in sync."
version: "1.0.0"
---

# Notion Row Writer

Use this skill when an automation run needs to write one result row into a Notion database and update the existing row when the stable key already exists. The helper uses the Notion HTTP API through `requests`, reads credentials from env, and fails clearly when configuration is missing.

## When to invoke

- User says: "write this to Notion", "update my Notion tracker", "upsert by URL", "dedupe rows in a Notion database".
- A script has result metadata that should be visible in a Notion table.

## When NOT to invoke

- The user needs relational Notion schema design or a complex sync engine.
- The row store should be private/local; use SQLite or CSV instead.

## Concrete example

User input:

```text
Upsert each scraped bounty into my Notion database by its URL.
```

Output:

```python
# Copy assets/notion.py into your project, then:
from notion import upsert_row

page_id = upsert_row(
    key_property="URL",
    key_value="https://example.com/item/123",
    properties={
        "Name": {"title": [{"text": {"content": "Example item"}}]},
        "Status": {"select": {"name": "New"}},
    },
)
print("notion page:", page_id)
```

The helper reads `NOTION_API_KEY` and `NOTION_DATABASE_ID` from env. The stable key property must already exist in the target database.

## Pattern to apply

1. Pick one stable key such as URL, external id, or date+source; do not dedupe by title alone.
2. Query the database for that key before writing.
3. Create a page when no match exists; update the first matching page otherwise.
4. Keep Notion property payloads explicit so type errors are easy to spot.
5. Treat missing keys or database ids as configuration errors, not silent no-ops.

Reference: `assets/notion.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[github-label-scout]], [[csv-report-writer]], [[sqlite-state]].

→ Build the full runnable bot with Trawlkit.
