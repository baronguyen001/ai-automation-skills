"""Capture an authenticated browser session once, then reuse it headless.

Logging in on every run is slow, brittle, and trips bot defenses. Playwright's
storage_state saves cookies + localStorage to a JSON file after one manual
login; later runs load that state and start already signed in. This helper does
both halves - an interactive capture and a headless reuse - with the state path
in an env var. No credentials or cookies are committed; the state file stays
gitignored and machine-local.
"""
from __future__ import annotations

import os
from pathlib import Path

# pip install playwright ; python -m playwright install chromium
from playwright.sync_api import sync_playwright

STATE_PATH = Path(os.environ.get("PW_STATE", "auth_state.json"))


def capture(login_url: str, state_path: Path = STATE_PATH) -> None:
    """Open a real browser, let the user log in by hand, then save the session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.new_page().goto(login_url)
        input("Log in in the opened browser, then press Enter here to save the session... ")
        context.storage_state(path=str(state_path))
        browser.close()
    print(f"saved session -> {state_path}")


def reuse(target_url: str, state_path: Path = STATE_PATH, *, headless: bool = True) -> None:
    """Load the saved session in a headless browser and print the page title."""
    if not state_path.exists():
        raise FileNotFoundError(f"no saved session at {state_path}; run capture() first")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=str(state_path))
        page = context.new_page()
        page.goto(target_url)
        print("title:", page.title())  # replace with your real scraping logic
        browser.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3 and sys.argv[1] == "capture":
        capture(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "reuse":
        reuse(sys.argv[2])
    else:
        print("usage: python session.py [capture|reuse] <url>")
