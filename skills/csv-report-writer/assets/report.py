"""Emit a schema'd CSV and a Markdown table from one column spec.

A run produces a list of result dicts; you usually want a CSV for spreadsheets
AND a Markdown table for a PR comment or chat digest. Declaring the columns
twice lets them drift. Here you declare each Column once - key, header, optional
formatter - and both writers consume the same list, so order and headers always
agree. CSV quoting is handled by the stdlib csv module; the Markdown writer
escapes pipes and newlines so a cell can never break the table. No pandas.
"""
from __future__ import annotations

import csv
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Row = Mapping[str, Any]


@dataclass(frozen=True)
class Column:
    """One report column: a dict key, a display header, and an optional formatter."""

    key: str
    header: str
    fmt: Callable[[Any], str] | None = None

    def render(self, row: Row) -> str:
        """Format this column's cell for a row; missing key -> empty cell."""
        if self.key not in row or row[self.key] is None:
            return ""
        value = row[self.key]
        return self.fmt(value) if self.fmt else str(value)


def _rows(columns: list[Column], rows: Iterable[Row]) -> list[list[str]]:
    return [[col.render(row) for col in columns] for row in rows]


def write_csv(path: str | Path, columns: list[Column], rows: Iterable[Row]) -> int:
    """Write rows to a CSV with the columns' headers; return the row count."""
    body = _rows(columns, rows)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([col.header for col in columns])
        writer.writerows(body)
    return len(body)


def _md_escape(cell: str) -> str:
    # A literal pipe or newline would break a Markdown table row.
    return cell.replace("|", "\\|").replace("\n", " ")


def to_markdown(columns: list[Column], rows: Iterable[Row]) -> str:
    """Render rows as a GitHub-flavored Markdown table string."""
    headers = [_md_escape(col.header) for col in columns]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for cells in _rows(columns, rows):
        lines.append("| " + " | ".join(_md_escape(c) for c in cells) + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    import io

    columns = [
        Column("symbol", "Symbol"),
        Column("score", "Score", fmt=lambda v: f"{v:.1f}"),
        Column("price_usd", "Price", fmt=lambda v: f"${v:,.4f}"),
        Column("note", "Note"),  # sometimes missing -> empty cell
    ]
    rows = [
        {"symbol": "ABC", "score": 8.4, "price_usd": 0.0123, "note": "a|b"},
        {"symbol": "XYZ", "score": 6.1, "price_usd": 1.5},
    ]

    # CSV self-test: round-trip through csv.reader and check escaping/order.
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([c.header for c in columns])
    w.writerows([[c.render(r) for c in columns] for r in rows])
    parsed = list(csv.reader(io.StringIO(buf.getvalue())))
    assert parsed[0] == ["Symbol", "Score", "Price", "Note"]
    assert parsed[1] == ["ABC", "8.4", "$0.0123", "a|b"]
    assert parsed[2][3] == ""  # missing note -> empty

    md = to_markdown(columns, rows)
    assert "a\\|b" in md  # pipe escaped in Markdown
    print(md)
