---
name: config-audit-checklist
description: "Audit a project for config drift before a backtest or deploy - compare the documented config snapshot against .env and README defaults, flag mismatches, and check the snapshot last-verified date. Use for config audit, params drift, pre-deploy checklist, or production config check."
---

# Config Audit Checklist

Use this skill before validating or deploying a project whose behavior depends on documented parameters. It forces the user to reconcile the live environment, the snapshot document, and README defaults before trusting results.

## When to invoke

- User says: "config audit" / "params drift" / "pre-deploy checklist" / "production config check"
- Code in the conversation uses: `.env`, `README` defaults, or a config snapshot document.

## When NOT to invoke

- The project has no config snapshot document yet; recommend creating one first.
- The project has no externally configurable parameters.

## Concrete example

User input:

```text
Audit this strategy config before I run the validation job.
```

Output:

```text
Auditing strategy config...
  ENTRY_COOLDOWN_HOURS:  README=12   .env=6    CONFIG.md=8     warn: 3-way drift
  STOP_LOSS_PCT:         README=-10  .env=-10  CONFIG.md=-10   ok
  CONFIG.md "Last verified": 2026-03-01 (89 days ago)         warn: stale (>30d)
Verdict: DO NOT backtest against README defaults. Reconcile the live config first.
```

## Pattern to apply

1. Find the config snapshot document, usually `PRODUCTION_CONFIG.md` or `CONFIG.md`.
2. Read the last verified date and flag stale snapshots.
3. Extract values from the snapshot, `.env`, and README defaults.
4. Report mismatches row by row and name the source of truth.
5. Refuse to proceed with validation until drift is reconciled.

Reference: `assets/checklist.md`.

## Source

Distilled from production use across the author's automation projects. v0.1.0.
See also: [[walk-forward-runner]].
