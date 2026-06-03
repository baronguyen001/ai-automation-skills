---
name: backtest-comparator
description: "Compare strategy variants across multiple years or folds and flag the ones that only look good on average - rank by mean fold score but surface dispersion and worst-fold so a variant that overfits one lucky period does not win silently. Use for compare backtest variants, flag overfit strategy, per-fold consistency, year by year backtest, or which parameter set is robust."
version: "1.0.0"
---

# Backtest Comparator

Use this skill when several strategy variants or parameter sets each have per-year (or per-fold) results and you need to pick the robust one, not the one with the highest average. A variant can win on the mean while quietly losing on an individual fold; this comparator ranks by mean but also reports standard deviation and the worst fold, then flags overfit and unstable variants so they can't slip through.

## When to invoke

- User says: "compare these backtest variants" / "which parameter set is robust" / "flag the overfit one" / "year-by-year results"
- Code in the conversation uses: a sweep that produced per-fold or per-year scores for multiple variants.

## When NOT to invoke

- You only have a single aggregate number per variant (no per-fold breakdown to judge consistency).
- The task is to build the validation split itself (use [[walk-forward-runner]] first, then compare its folds here).

## Concrete example

User input:

```text
Three variants, four years of returns each. Tell me which is actually robust vs which just got lucky one year.
```

Output:

```text
variant              mean      std    worst  verdict
------------------------------------------------------
cross_only          0.188    0.027    0.150  robust
macd_filter         0.095    0.011    0.080  robust
pullback_ema21      0.075    0.205   -0.120  OVERFIT (positive mean, loses on a fold)
```

Code:

```python
# Copy assets/compare.py into your project, then:
from compare import compare_variants, format_table

folds = {
    "cross_only":     [0.18, 0.22, 0.15, 0.20],
    "macd_filter":    [0.10, 0.09, 0.11, 0.08],
    "pullback_ema21": [0.40, -0.12, 0.05, -0.03],
}
print(format_table(compare_variants(folds)))
```

## Pattern to apply

1. Collect per-fold scores per variant in chronological order (one number per year/fold).
2. Compute mean, standard deviation, worst fold, and best fold for each variant.
3. Rank by mean, but never decide on mean alone.
4. Flag `OVERFIT` when the mean is positive yet a fold is negative; flag `UNSTABLE` when dispersion exceeds the mean.
5. Prefer the variant whose worst fold still holds up over the one with the flashiest average.

Reference: `assets/compare.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[walk-forward-runner]], [[config-audit-checklist]].

→ Build the full runnable bot with Trawlkit.
