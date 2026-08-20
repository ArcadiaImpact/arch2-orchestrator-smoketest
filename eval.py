"""Toy smoke-test eval: median of values in sample.csv. Reads ARCH_DATA_ROOT.

Reports the median instead of the arithmetic-mean baseline (see
attempts/median/RESEARCH_LOG.md for why), and records the baseline mean
alongside it in `metrics` so the two can be compared without re-running
anything.
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import sys
from pathlib import Path


def main() -> int:
    data_root = Path(os.environ["ARCH_DATA_ROOT"])
    output_path = Path(os.environ["ARCH_EVAL_OUTPUT"])

    csv_path = data_root / "sample.csv"
    with csv_path.open() as f:
        values = [float(row["value"]) for row in csv.DictReader(f)]

    mean_baseline = sum(values) / len(values)
    score = statistics.median(values)
    record = {
        "score": score,
        "metrics": {"n": len(values), "mean_baseline": mean_baseline},
        "notes": "score is the median; mean_baseline is the direction-1 reference for comparison",
    }
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
