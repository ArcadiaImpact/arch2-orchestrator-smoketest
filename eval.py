"""Toy smoke-test eval: mean of values in sample.csv. Reads ARCH_DATA_ROOT."""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from pathlib import Path


def main() -> int:
    data_root = Path(os.environ["ARCH_DATA_ROOT"])
    output_path = Path(os.environ["ARCH_EVAL_OUTPUT"])

    csv_path = data_root / "sample.csv"
    with csv_path.open() as f:
        values = [float(row["value"]) for row in csv.DictReader(f)]

    plain_sum = sum(values)
    compensated_sum = math.fsum(values)
    score = compensated_sum / len(values)
    record = {
        "score": score,
        "metrics": {
            "n": len(values),
            "plain_sum": plain_sum,
            "compensated_sum": compensated_sum,
            "sum_diff": compensated_sum - plain_sum,
        },
        "notes": "",
    }
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
