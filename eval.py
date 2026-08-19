"""Toy smoke-test eval: median of values in sample.csv (attempt `median`,
a hypothesis beyond the two seeded in problem.md). Reads ARCH_DATA_ROOT.

problem.md seeds two directions: (1) the plain arithmetic mean, and (2) a
trimmed/robust mean (an average of a subset of the sorted values, tested in
the sibling `trimmed-mean` attempt). This attempt tests a third, structurally
different estimator of central tendency: the median, the middle value of the
sorted data (or the average of the two middle values for even n). Unlike a
trimmed mean, the median does not average multiple data points at all for
odd n -- it picks a single order statistic and ignores the magnitude of
every other value entirely. That makes it a distinct test of the same
underlying question (problem.md: "is there a statistic more correct than
the arithmetic mean for this task") via a different mechanism than trimming.

The `metrics` field also reports the untouched arithmetic mean so the two
can be compared side by side in local `arch eval` runs and CI logs (not
published on held-out PR comments per .arch/config.toml's empty
public_metrics allow-list).
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def main() -> int:
    data_root = Path(os.environ["ARCH_DATA_ROOT"])
    output_path = Path(os.environ["ARCH_EVAL_OUTPUT"])

    csv_path = data_root / "sample.csv"
    with csv_path.open() as f:
        values = [float(row["value"]) for row in csv.DictReader(f)]

    arithmetic_mean = sum(values) / len(values)
    score = median(values)
    record = {
        "score": score,
        "metrics": {"n": len(values), "arithmetic_mean": arithmetic_mean},
        "notes": "median",
    }
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
