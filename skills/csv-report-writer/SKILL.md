---
name: csv-report-writer
description: "Turn a run's list of result dicts into a schema'd CSV and a Markdown table from one column spec - declare columns once, emit both, with stable ordering and safe escaping, stdlib only, no pandas. Use when the user asks to write results to CSV, export a report, make a markdown summary table, or save a run's output as a spreadsheet."
version: "1.0.0"
---

# CSV Report Writer

Use this skill when a job produces a list of result rows and you want a tidy CSV for spreadsheets plus a Markdown table for a PR comment or Telegram digest - from a single column definition, so the two outputs never drift. You declare the columns (key, header, optional formatter) once; the helper emits both, in a stable column order, with proper CSV quoting and pipe-escaping for Markdown. No pandas.

## When to invoke

- User says: "write the results to a CSV", "export a report", "make a markdown table of this", "save the run output as a spreadsheet".
- Code in the conversation has a `list[dict]` (or list of objects) it currently prints ad hoc.

## When NOT to invoke

- The data needs real dataframe work - joins, group-bys, pivots; reach for pandas/polars instead.
- A single scalar result, where a CSV/table is overkill.

## Concrete example

User input:

```text
I have a list of scanned tokens with a score and price. Save a CSV and also give me a markdown table for the Telegram digest.
```

Output:

```python
# Copy assets/report.py into your project, then:
from report import Column, write_csv, to_markdown

columns = [
    Column("symbol", "Symbol"),
    Column("score", "Score", fmt=lambda v: f"{v:.1f}"),
    Column("price_usd", "Price", fmt=lambda v: f"${v:,.4f}"),
]
rows = [
    {"symbol": "ABC", "score": 8.4, "price_usd": 0.0123},
    {"symbol": "XYZ", "score": 6.1, "price_usd": 1.5},
]

write_csv("scan.csv", columns, rows)        # schema'd CSV, stable column order
print(to_markdown(columns, rows))           # same columns, Markdown table
```

Both outputs use the exact same columns in the exact same order, so the CSV and the digest table always agree.

## Pattern to apply

1. Declare each `Column(key, header, fmt=...)` once; both writers consume the same list, so headers and order stay in sync.
2. Keep the column order stable and explicit - do not rely on dict insertion order of arbitrary rows.
3. Let the `fmt` callable own presentation (currency, rounding); store raw values in the row dicts.
4. Use `csv.writer` for correct quoting; escape `|` and newlines for the Markdown table so it never breaks layout.
5. Treat a missing key as an empty cell rather than crashing, so partial rows still report.

Reference: `assets/report.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[pr-body-formatter]], [[sqlite-state]], [[telegram-alerter]].

→ Build the full runnable bot with Trawlkit.
