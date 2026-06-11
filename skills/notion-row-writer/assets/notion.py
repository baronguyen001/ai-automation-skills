"""Upsert a row into a Notion database by a stable key.

Env-only config: NOTION_API_KEY and NOTION_DATABASE_ID. The database must have a
property matching key_property. This helper uses requests and raises clear
configuration errors when credentials are absent.
"""
from __future__ import annotations

import os
from typing import Any

NOTION_VERSION = "2022-06-28"
API_BASE = "https://api.notion.com/v1"


class NotionConfigError(RuntimeError):
    """Raised when env vars or dependencies are missing."""


def _requests() -> Any:
    try:
        import requests  # type: ignore
    except ImportError as exc:
        raise NotionConfigError("install requests to use notion-row-writer") from exc
    return requests


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise NotionConfigError(f"missing required env var: {name}")
    return value


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_env('NOTION_API_KEY')}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _key_filter(key_property: str, key_value: str) -> dict[str, Any]:
    return {"property": key_property, "rich_text": {"equals": key_value}}


def find_page(database_id: str, key_property: str, key_value: str) -> str | None:
    """Return the first page id matching key_property == key_value."""
    requests = _requests()
    resp = requests.post(
        f"{API_BASE}/databases/{database_id}/query",
        headers=_headers(),
        json={"filter": _key_filter(key_property, key_value), "page_size": 1},
        timeout=20,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0]["id"] if results else None


def upsert_row(
    *,
    key_property: str,
    key_value: str,
    properties: dict[str, Any],
    database_id: str | None = None,
) -> str:
    """Create or update a Notion page and return the page id."""
    requests = _requests()
    db_id = database_id or _env("NOTION_DATABASE_ID")
    props = dict(properties)
    props.setdefault(key_property, {"rich_text": [{"text": {"content": key_value}}]})

    page_id = find_page(db_id, key_property, key_value)
    if page_id:
        resp = requests.patch(
            f"{API_BASE}/pages/{page_id}",
            headers=_headers(),
            json={"properties": props},
            timeout=20,
        )
    else:
        resp = requests.post(
            f"{API_BASE}/pages",
            headers=_headers(),
            json={"parent": {"database_id": db_id}, "properties": props},
            timeout=20,
        )
    resp.raise_for_status()
    return resp.json()["id"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upsert a simple Notion row by key")
    parser.add_argument("key_property")
    parser.add_argument("key_value")
    parser.add_argument("--title-property", default="Name")
    parser.add_argument("--title", default="Automation result")
    args = parser.parse_args()

    page = upsert_row(
        key_property=args.key_property,
        key_value=args.key_value,
        properties={
            args.title_property: {"title": [{"text": {"content": args.title}}]},
        },
    )
    print(page)
