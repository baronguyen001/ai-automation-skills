"""Scan a public GitHub repo for open issues with a given label, skipping the
ones already taken (assignees present) and the pull requests the issues
endpoint mixes in.

Uses the public REST API. No token is required for low volume; set GITHUB_TOKEN
in the environment only to raise the rate limit. This ships no hidden repo
list - you pass the repos you care about.
"""
from __future__ import annotations

import json
import os
import urllib.request
from urllib.parse import quote


def _get(url: str) -> list[dict]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-label-scout",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def scout_label(repo: str, label: str, *, max_results: int = 30) -> list[dict[str, object]]:
    """Return open, UNASSIGNED issues in `owner/repo` carrying `label`."""
    url = (
        f"https://api.github.com/repos/{repo}/issues"
        f"?state=open&labels={quote(label)}&per_page={max_results}"
    )
    rows: list[dict[str, object]] = []
    for issue in _get(url):
        if "pull_request" in issue:
            continue  # the issues endpoint also returns PRs; drop them
        if issue.get("assignees"):
            continue  # already taken - skip per the assignee-first rule
        rows.append({
            "number": issue["number"],
            "title": issue["title"],
            "url": issue["html_url"],
            "comments": issue.get("comments", 0),
        })
    return rows


if __name__ == "__main__":
    for row in scout_label("octocat/Hello-World", "good first issue"):
        print(f"#{row['number']:<5} {row['title']}  ({row['comments']} comments)  {row['url']}")
