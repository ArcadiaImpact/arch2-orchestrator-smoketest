"""Standalone verification for the arithmetic-mean baseline (research direction 1).

Independently recomputes the mean of `value` in a sample.csv using a
different code path than eval.py (statistics.mean instead of sum/len) and
asserts the two agree. This is a sanity check on the reference computation,
not a replacement for eval.py — eval.py itself is left untouched so the
scored artifact for this attempt is exactly the baseline the task ships
with.

Usage: python3 attempts/mean-baseline/verify_mean.py <path-to-sample.csv>
Defaults to data/public/sample.csv if no path is given.
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path


def load_values(csv_path: Path) -> list[float]:
    with csv_path.open() as f:
        return [float(row["value"]) for row in csv.DictReader(f)]


def main() -> int:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/public/sample.csv")
    values = load_values(csv_path)

    direct = sum(values) / len(values)
    via_stdlib = statistics.mean(values)

    print(f"n={len(values)} values={values}")
    print(f"sum(values)/len(values) = {direct}")
    print(f"statistics.mean(values) = {via_stdlib}")

    assert direct == via_stdlib, (
        f"baseline mismatch: sum/len gave {direct}, statistics.mean gave {via_stdlib}"
    )
    print("OK: both computations agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
