"""Independent reproduction of the mean computation, for attempt
`arithmetic-mean`.

This does not change how `eval.py` scores a PR (`eval.py` already sums the
`value` column and divides by row count). It exists so the arithmetic-mean
hypothesis is a checked-in, reproducible artifact rather than just an
assertion in the research log: run it against any `sample.csv` and it prints
the same number `eval.py` would report as `score`.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path


def arithmetic_mean(csv_path: Path) -> float:
    with csv_path.open() as f:
        values = [float(row["value"]) for row in csv.DictReader(f)]
    return sum(values) / len(values)


if __name__ == "__main__":
    root = Path(os.environ.get("ARCH_DATA_ROOT", "data/public"))
    mean = arithmetic_mean(root / "sample.csv")
    print(f"arithmetic mean: {mean}")
    sys.exit(0)
