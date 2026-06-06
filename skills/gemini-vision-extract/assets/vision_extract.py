"""Structured extraction from an image with Gemini, validated against a schema.

Point it at an image (a receipt, invoice, screenshot, chart) and get back typed
JSON, not prose. The Gemini call uses response_mime_type=application/json plus a
Pydantic response_schema, so the model is constrained to your fields and the
result parses cleanly. The API key comes only from the environment. SDK =
google-genai (the current unified SDK).
"""
from __future__ import annotations

import os
from pathlib import Path

# pip install google-genai pydantic
from google import genai
from google.genai import types
from pydantic import BaseModel


class Receipt(BaseModel):
    """Default schema; swap in your own Pydantic model for other documents."""

    merchant: str
    date: str | None = None
    total: float | None = None
    currency: str | None = None
    items: list[str] = []


def extract(
    image_path: str | Path,
    schema: type[BaseModel] = Receipt,
    model: str = "gemini-2.5-flash",
) -> BaseModel:
    """Extract structured fields from one image into a validated Pydantic model."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    image = Path(image_path)
    mime = "image/png" if image.suffix.lower() == ".png" else "image/jpeg"

    resp = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=image.read_bytes(), mime_type=mime),
            "Extract the fields defined by the schema. Use null when a field is absent.",
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )
    # resp.parsed is already a validated `schema` instance; fall back to raw text.
    return resp.parsed if resp.parsed is not None else schema.model_validate_json(resp.text)


if __name__ == "__main__":
    import sys

    if "GEMINI_API_KEY" not in os.environ:
        raise SystemExit("set GEMINI_API_KEY to enable")
    path = sys.argv[1] if len(sys.argv) > 1 else "receipt.png"
    print(extract(path).model_dump_json(indent=2))
