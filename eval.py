"""Toy smoke-test eval: mean of values in sample.csv. Reads ARCH_DATA_ROOT."""
from __future__ import annotations

import csv
import json
import os
import sys
from decimal import Decimal
from pathlib import Path


def main() -> int:
    data_root = Path(os.environ["ARCH_DATA_ROOT"])
    output_path = Path(os.environ["ARCH_EVAL_OUTPUT"])

    csv_path = data_root / "sample.csv"
    with csv_path.open() as f:
        raw_values = [row["value"] for row in csv.DictReader(f)]

    # Decimal is constructed from the original string, not from a float, so
    # values like "0.1" keep their exact base-10 representation instead of
    # picking up the binary-float rounding that `float("0.1")` introduces.
    decimal_values = [Decimal(v) for v in raw_values]
    decimal_mean = sum(decimal_values) / Decimal(len(decimal_values))

    # Binary-float mean computed the same way as the arithmetic-mean
    # baseline, kept only as an internal cross-check against decimal_mean.
    float_mean = sum(float(v) for v in raw_values) / len(raw_values)

    score = float(decimal_mean)
    record = {
        "score": score,
        "metrics": {
            "n": len(decimal_values),
            "decimal_mean": str(decimal_mean),
            "float_mean": float_mean,
            "decimal_float_agree": decimal_mean == Decimal(float_mean),
        },
        "notes": "mean computed with decimal.Decimal from the original CSV strings",
    }
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
