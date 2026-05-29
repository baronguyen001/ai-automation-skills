---
name: algora-bounty-scout
description: "Scout public Algora org bounty boards at algora.io/<org>/bounties?status=open - parse amount and linked GitHub issue, dedupe, then filter already-assigned issues, saturated races, joke bounties, dead-lane orgs, and maintainer comments that say the bounty is inactive. Use for scout algora, find OSS bounties, or open source bounty hunting."
---

# Algora Bounty Scout

Use this skill when a user wants to find public Algora bounties and avoid wasting time on issues that are not realistically claimable. It teaches the scouting technique and generic pitfall filters without shipping a curated org list.

## When to invoke

- User says: "scout algora" / "find OSS bounties" / "open source bounty hunting"
- Code in the conversation uses: HTTP scraping, GitHub issue metadata, or bounty triage.

## When NOT to invoke

- The user wants private or paid bounty platforms.
- The user already has a specific GitHub issue and only needs implementation help.

## Concrete example

User input:

```text
Scout these public Algora org boards and show only viable bounties: acme, samplelab, widgetco.
```

Output:

```text
algora scout (3 orgs) -> 9 raw bounties
  ok   $300  acme/webapp#812     "Add OIDC provider" (0 open PRs, unassigned)
  ok   $150  acme/cli#77         "Fix flaky retry test" (unassigned)
  skip $400  acme/webapp#640     assigned to another contributor
  skip $250  samplelab/api#92    maintainer comment says bounty is inactive
  skip $100  widgetco/quest#1    submission game, not a mergeable issue
  -> 3 viable
```

## Pattern to apply

1. Start from user-provided public org slugs; do not use a hidden curated list.
2. Probe `https://algora.io/<org>/bounties?status=open`.
3. Parse amount, title, and linked GitHub issue URL.
4. Dedupe by GitHub issue URL.
5. Fetch GitHub issue metadata: assignees, linked PRs, recent maintainer comments.
6. Apply the pitfall filters before writing any implementation code.

Reference: `assets/pitfall_list.md`.

## Source

Distilled from production use across the author's automation projects. v0.1.0.
See also: [[pr-body-formatter]].
