---
name: github-label-scout
description: "Scan a public GitHub repo for open issues carrying a given label and drop the ones already taken - skips pull requests returned by the issues endpoint and any issue with assignees - using the public REST API with no token required. Use for find github issues by label, good first issue scout, skip assigned issues, github issue triage, or open source contribution finder."
version: "1.0.0"
---

# GitHub Label Scout

Use this skill when a user wants to find claimable open issues in a public repo by label - "good first issue", "help wanted", "bug" - without wasting time on issues someone already owns. It hits the public REST API, filters out the pull requests the issues endpoint mixes in, and skips anything with an assignee so you only see open lanes. No token is needed for low volume; set one in the env only to raise the rate limit.

## When to invoke

- User says: "find issues by label" / "good first issue scout" / "skip assigned issues" / "open-source contribution finder"
- Code in the conversation uses: GitHub issue triage, label filtering, or contribution discovery.

## When NOT to invoke

- The user wants paid bounty boards (use [[algora-bounty-scout]] for that).
- The user already has one specific issue and only needs implementation help.

## Concrete example

User input:

```text
Show me unassigned "good first issue" tickets in octocat/Hello-World.
```

Output:

```python
# Copy assets/scout.py into your project, then:
from scout import scout_label

for row in scout_label("octocat/Hello-World", "good first issue"):
    print(f"#{row['number']} {row['title']} ({row['comments']} comments) {row['url']}")
# #142 Fix typo in README (1 comments) https://github.com/octocat/Hello-World/issues/142
# #156 Add retry to client (0 comments) https://github.com/octocat/Hello-World/issues/156
```

The helper reads an optional `GITHUB_TOKEN` from the environment purely to raise the rate limit; it works unauthenticated.

## Pattern to apply

1. Query `GET /repos/{owner}/{repo}/issues?state=open&labels=<label>`.
2. Drop any item that has a `pull_request` key - the issues endpoint returns PRs too.
3. Skip any issue with a non-empty `assignees` array (assignee-first rule: assigned = already taken).
4. Return number, title, URL, and comment count so you can prioritize.
5. Add `GITHUB_TOKEN` from env only for rate-limit headroom; never hardcode a token.

Reference: `assets/scout.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[algora-bounty-scout]], [[pr-body-formatter]].

→ Build the full runnable bot with Trawlkit.
