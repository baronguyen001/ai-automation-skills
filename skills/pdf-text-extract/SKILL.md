---
name: pdf-text-extract
description: "Extract text and simple table-like rows from a PDF for downstream AI without OCR binaries. Use when the user asks to read a PDF, turn a PDF into text, pull simple tables from statements/reports, or feed PDF content into an LLM pipeline."
version: "1.0.0"
---

# PDF Text Extract

Use this skill when a workflow needs machine-readable text from a digital PDF before summarization, classification, or structured extraction. The helper uses pure-Python PDF libraries when available and includes a simple line-based table detector for downstream cleanup.

## When to invoke

- User says: "extract text from this PDF", "feed a PDF to AI", "pull tables from this report", "read this statement".
- The PDF already contains selectable text and does not require OCR.

## When NOT to invoke

- The PDF is a scanned image; use an OCR workflow instead.
- The user needs pixel-perfect table reconstruction with merged cells and layout fidelity.

## Concrete example

User input:

```text
Extract the text and rough tables from this PDF so Gemini can summarize it.
```

Output:

```python
# Copy assets/extract.py into your project, then:
from extract import extract_pdf

doc = extract_pdf("downloads/report.pdf")
print(doc["text"][:2000])
for table in doc["tables"]:
    print(table["page"], table["rows"][:3])
```

Install either `pypdf` or `pdfminer.six` in the target project. No OCR binary is required, and the helper fails clearly when the PDF has no extractable text.

## Pattern to apply

1. Prefer digital text extraction first; do not add OCR unless the source is scanned.
2. Preserve page boundaries so downstream prompts can cite page numbers.
3. Keep table extraction simple: split rows on tabs or repeated spaces, then let a later schema pass normalize columns.
4. Cap text sent to an LLM by page/range when the PDF is long.
5. Fail loudly when no text is found instead of sending an empty prompt downstream.

Reference: `assets/extract.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[gemini-structured-output]], [[csv-report-writer]], [[s3-uploader]].

→ Build the full runnable bot with Trawlkit.
