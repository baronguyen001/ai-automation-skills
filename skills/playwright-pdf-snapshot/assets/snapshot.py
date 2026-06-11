"""Render a URL to PDF and/or PNG with headless Playwright.

No cookies, tokens, or site-specific headers are embedded. For authenticated
pages, combine this with a gitignored storage_state file from
playwright-login-session and pass it from your own project code.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class SnapshotError(RuntimeError):
    """Raised when Playwright is missing or the capture fails."""


def snapshot(
    url: str,
    *,
    out_dir: str | Path = "artifacts",
    name: str = "snapshot",
    pdf: bool = True,
    png: bool = True,
    wait_until: str = "networkidle",
    viewport: tuple[int, int] = (1440, 1200),
    extra_http_headers: dict[str, str] | None = None,
) -> dict[str, str]:
    """Render url and return output paths for the generated artifacts."""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError as exc:
        raise SnapshotError(
            "install playwright and run: python -m playwright install chromium"
        ) from exc

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context_kwargs: dict[str, Any] = {
            "viewport": {"width": viewport[0], "height": viewport[1]},
        }
        if extra_http_headers:
            context_kwargs["extra_http_headers"] = extra_http_headers
        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        page.goto(url, wait_until=wait_until, timeout=60_000)

        if pdf:
            pdf_path = out / f"{name}.pdf"
            page.pdf(path=str(pdf_path), print_background=True, format="A4")
            paths["pdf"] = str(pdf_path)
        if png:
            png_path = out / f"{name}.png"
            page.screenshot(path=str(png_path), full_page=True)
            paths["png"] = str(png_path)

        browser.close()

    return paths


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Render a URL to PDF/PNG with Playwright")
    parser.add_argument("url")
    parser.add_argument("--out-dir", default="artifacts")
    parser.add_argument("--name", default="snapshot")
    parser.add_argument("--pdf", action="store_true")
    parser.add_argument("--png", action="store_true")
    args = parser.parse_args()

    make_pdf = args.pdf or not args.png
    make_png = args.png or not args.pdf
    print(snapshot(args.url, out_dir=args.out_dir, name=args.name, pdf=make_pdf, png=make_png))
