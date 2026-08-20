"""Toy smoke-test eval: median of values in sample.csv. Reads ARCH_DATA_ROOT."""
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

    mean = sum(values) / len(values)
    median = statistics.median(values)
    score = median
    record = {
        "score": score,
        "metrics": {"n": len(values), "mean": mean, "median": median},
        "notes": "",
    }
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
