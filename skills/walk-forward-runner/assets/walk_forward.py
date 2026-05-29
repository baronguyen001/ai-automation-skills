from collections.abc import Iterable, Iterator
from datetime import datetime, timedelta


Window = tuple[datetime, datetime, datetime, datetime]


def walk_forward_folds(
    timestamps_sorted: Iterable[datetime],
    train: timedelta,
    val: timedelta,
    step: timedelta,
) -> Iterator[Window]:
    """Yield rolling train/validation windows with no future leakage."""
    timestamps = list(timestamps_sorted)
    if not timestamps:
        return

    start = timestamps[0]
    end = timestamps[-1]
    current = start

    while current + train + val <= end:
        train_start = current
        train_end = current + train
        val_start = train_end
        val_end = train_end + val

        assert val_start >= train_end, "LEAKAGE: validation starts before train ends"
        yield train_start, train_end, val_start, val_end
        current += step


def verdict(train_rank: int, val_rank: int, n: int) -> str:
    half = (n + 1) // 2
    if train_rank == 1 and val_rank == 1:
        return "STRONG ROBUST"
    if train_rank <= half and val_rank <= half:
        return "robust"
    if train_rank <= half and val_rank > half:
        return "OVERFIT (good train, bad val)"
    if train_rank > half and val_rank <= half:
        return "underperformer on train"
    return "weak both"
