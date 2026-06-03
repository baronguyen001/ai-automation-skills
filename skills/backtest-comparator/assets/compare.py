"""Compare strategy variants across multiple years/folds and flag the ones
that only look good on average but fall apart on individual folds.

Input is a mapping of variant name -> per-fold scores (one score per
year/fold, in chronological order). The comparator ranks by mean but surfaces
dispersion and worst-fold, so a variant that overfits a single lucky period
does not win silently.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev


@dataclass
class VariantStat:
    name: str
    mean: float
    std: float
    worst: float
    best: float
    flag: str


def _flag(m: float, s: float, worst: float, best: float) -> str:
    if worst < 0 <= m:
        return "OVERFIT (positive mean, loses on a fold)"
    if m != 0 and s > abs(m):
        return "UNSTABLE (dispersion exceeds mean)"
    if worst > 0 and s <= abs(m):
        return "robust"
    return "weak"


def compare_variants(scores_by_variant: dict[str, list[float]]) -> list[VariantStat]:
    """Rank variants by mean fold score and flag likely-overfit ones."""
    stats: list[VariantStat] = []
    for name, scores in scores_by_variant.items():
        if not scores:
            continue
        m = mean(scores)
        s = pstdev(scores) if len(scores) > 1 else 0.0
        stats.append(VariantStat(name, m, s, min(scores), max(scores), _flag(m, s, min(scores), max(scores))))

    stats.sort(key=lambda v: v.mean, reverse=True)
    return stats


def format_table(stats: list[VariantStat]) -> str:
    """Render the comparison as a fixed-width table."""
    header = f"{'variant':<18}{'mean':>9}{'std':>9}{'worst':>9}  verdict"
    lines = [header, "-" * len(header)]
    for v in stats:
        lines.append(f"{v.name:<18}{v.mean:>9.3f}{v.std:>9.3f}{v.worst:>9.3f}  {v.flag}")
    return "\n".join(lines)


if __name__ == "__main__":
    folds = {
        "cross_only":     [0.18, 0.22, 0.15, 0.20],
        "macd_filter":    [0.10, 0.09, 0.11, 0.08],
        "pullback_ema21": [0.40, -0.12, 0.05, -0.03],
    }
    print(format_table(compare_variants(folds)))
