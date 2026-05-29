---
name: walk-forward-runner
description: "Set up a leakage-free walk-forward rolling split for any time-series model or strategy and flag overfit parameters where a value ranks high on train but low on validation. Use for walk forward validation, time series cross validation, no leakage split, rolling backtest, or parameter overfit checks."
---

# Walk-Forward Runner

Use this skill when a time-series model or rule-based strategy needs chronological validation without leakage. It gives the user rolling train/validation windows and a simple rank-divergence verdict for parameter robustness.

## When to invoke

- User says: "walk forward validation" / "time series cross validation" / "no leakage split"
- Code in the conversation uses: timestamped rows, rolling windows, chronological model evaluation, or parameter sweeps.

## When NOT to invoke

- The dataset is too short for multiple folds.
- The task is ordinary shuffled cross-validation on independent rows.

## Concrete example

User input:

```text
I tested lookback values on 3 years of daily rows. Flag which settings are overfit.
```

Output:

```text
Param value   Train rank   Val rank   Verdict
lookback=20        1            1      STRONG ROBUST
lookback=50        2            6      OVERFIT (good train, bad val)
lookback=10        5            3      weak both
```

Code:

```python
from datetime import timedelta

# Copy assets/walk_forward.py into your project, then:
from walk_forward import walk_forward_folds, verdict

folds = list(walk_forward_folds(rows["timestamp"], timedelta(days=365), timedelta(days=90), timedelta(days=30)))
label = verdict(train_rank=2, val_rank=6, n=6)
```

## Pattern to apply

1. Sort rows by timestamp before splitting.
2. Roll fixed train and validation windows forward by a step size.
3. Assert validation starts at or after train end.
4. Rank each parameter on train and validation.
5. Flag train-good/validation-bad divergence as overfit.

Reference: `assets/walk_forward.py`.

## Source

Distilled from production use across the author's automation projects. v0.1.0.
See also: [[config-audit-checklist]].
