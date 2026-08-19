"""Toy smoke-test eval: trimmed mean of values in sample.csv (attempt
`trimmed-mean`, direction 2 in problem.md). Reads ARCH_DATA_ROOT.

Direction 1 (the plain arithmetic mean) is the base-branch behavior and is
re-verified in the sibling `arithmetic-mean` attempt. This attempt swaps the
statistic for a trimmed mean: sort the values, drop the top and bottom
round(TRIM_FRACTION * n) of them, and average what's left. The `metrics`
field also reports the untouched arithmetic mean so the two can be compared
side by side (metrics are not published on held-out PR comments per
.arch/config.toml, but are visible in local `arch eval` runs and CI logs).
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

TRIM_FRACTION = 0.2  # drop this fraction of values from each tail


def trimmed_mean(values: list[float], trim_fraction: float) -> float:
    ordered = sorted(values)
    n = len(ordered)
    k = round(trim_fraction * n)
    kept = ordered[k : n - k] if n - 2 * k > 0 else ordered
    return sum(kept) / len(kept)


def main() -> int:
    data_root = Path(os.environ["ARCH_DATA_ROOT"])
    output_path = Path(os.environ["ARCH_EVAL_OUTPUT"])

    csv_path = data_root / "sample.csv"
    with csv_path.open() as f:
        values = [float(row["value"]) for row in csv.DictReader(f)]

    arithmetic_mean = sum(values) / len(values)
    score = trimmed_mean(values, TRIM_FRACTION)
    record = {
        "score": score,
        "metrics": {"n": len(values), "arithmetic_mean": arithmetic_mean},
        "notes": f"trimmed mean, trim_fraction={TRIM_FRACTION}",
    }
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
