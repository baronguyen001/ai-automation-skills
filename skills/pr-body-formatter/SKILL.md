---
name: pr-body-formatter
description: "Generate a complete GitHub PR body with Summary, Changes, How tested, Test plan, and issue link from a branch diff plus issue reference, and never ship a placeholder body. Use for pr body template, format pr description, write a PR description, or API/CLI PR creation."
---

# PR Body Formatter

Use this skill when opening a GitHub PR from a diff summary and issue reference. It produces a filled PR body and rejects leftover TODO-style placeholders before the PR is marked ready.

## When to invoke

- User says: "pr body template" / "format pr description" / "write a PR description"
- Code in the conversation uses: GitHub CLI/API PR creation or a branch diff summary.

## When NOT to invoke

- The target repository has its own PR template; use the maintainer's template instead.
- The user only wants a commit message.

## Concrete example

User input:

```text
Write the PR body for a branch that adds OIDC auth and closes acme/webapp#812.
```

Output:

```markdown
## Summary
Adds an OIDC provider option to the auth module, closing acme/webapp#812.

## Changes
- `auth/oidc.py`: new `OIDCProvider` implementing the existing `AuthProvider` protocol
- `auth/factory.py`: register `oidc` in `PROVIDERS`
- `tests/test_oidc.py`: token exchange and error-path coverage

## How tested
- `pytest tests/test_oidc.py` - 7 passing
- Manual: ran the local auth flow against a Keycloak dev realm and verified token round-trip

## Test plan
- [ ] CI green
- [ ] Maintainer confirms OIDC config keys match docs

Closes acme/webapp#812
```

## Pattern to apply

1. Inspect the diff summary and the linked issue.
2. Fill every section with specific file names, behavior, and test evidence.
3. Include the closing issue reference exactly once.
4. Search the body for `TODO`, `TBD`, and copied instruction text before returning it.
5. Refuse to emit a ready PR body if any placeholder remains.

Reference: `assets/template.md`.

## Source

Distilled from production use across the author's automation projects. v0.1.0.
See also: [[algora-bounty-scout]].
