"""Extract text and simple table-like rows from digital PDFs.

This intentionally does not perform OCR. Install either pypdf or pdfminer.six
in the target project. Tables are detected conservatively from text lines with
tabs or repeated spaces; downstream code should normalize the final schema.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class PdfExtractError(RuntimeError):
    """Raised when no supported PDF parser is installed or no text is found."""


def _extract_with_pypdf(path: Path) -> list[str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise PdfExtractError("pypdf is not installed") from exc

    reader = PdfReader(str(path))
    return [(page.extract_text() or "") for page in reader.pages]


def _extract_with_pdfminer(path: Path) -> list[str]:
    try:
        from pdfminer.high_level import extract_text  # type: ignore
    except ImportError as exc:
        raise PdfExtractError("pdfminer.six is not installed") from exc

    text = extract_text(str(path)) or ""
    return text.split("\f")


def _split_table_line(line: str) -> list[str]:
    if "\t" in line:
        return [part.strip() for part in line.split("\t") if part.strip()]
    return [part.strip() for part in re.split(r"\s{2,}", line.strip()) if part.strip()]


def simple_tables_from_text(text: str, *, min_columns: int = 2) -> list[list[list[str]]]:
    """Group consecutive table-like lines into rough tables."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for raw in text.splitlines():
        cols = _split_table_line(raw)
        if len(cols) >= min_columns:
            current.append(cols)
            continue
        if len(current) >= 2:
            tables.append(current)
        current = []
    if len(current) >= 2:
        tables.append(current)
    return tables


def extract_pdf(path: str | Path) -> dict[str, Any]:
    """Return {"text": str, "pages": [...], "tables": [...]} for a digital PDF."""
    pdf = Path(path)
    if not pdf.is_file():
        raise FileNotFoundError(pdf)

    errors: list[str] = []
    pages: list[str] = []
    for extractor in (_extract_with_pypdf, _extract_with_pdfminer):
        try:
            pages = extractor(pdf)
            if any(page.strip() for page in pages):
                break
        except PdfExtractError as exc:
            errors.append(str(exc))
    else:
        raise PdfExtractError("; ".join(errors) or "no PDF text extractor available")

    if not any(page.strip() for page in pages):
        raise PdfExtractError("no extractable text found; this may be a scanned PDF")

    table_blocks: list[dict[str, Any]] = []
    for page_num, page_text in enumerate(pages, start=1):
        for rows in simple_tables_from_text(page_text):
            table_blocks.append({"page": page_num, "rows": rows})

    return {
        "text": "\n\n".join(page.strip() for page in pages if page.strip()),
        "pages": [{"page": i, "text": text} for i, text in enumerate(pages, start=1)],
        "tables": table_blocks,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract text and rough tables from a PDF")
    parser.add_argument("pdf")
    parser.add_argument("--json", action="store_true", help="print full JSON instead of text")
    args = parser.parse_args()
    result = extract_pdf(args.pdf)
    print(json.dumps(result, indent=2) if args.json else result["text"])
