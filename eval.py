"""Toy smoke-test eval: mean of values in sample.csv. Reads ARCH_DATA_ROOT."""
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

    # `statistics.mean` does not sum floats directly. Internally it converts
    # each input to an exact `fractions.Fraction`, sums those exactly (a
    # Fraction sum has no rounding error at any step, since fractions have
    # unbounded-precision numerators/denominators), and only converts back to
    # `float` once at the very end. That is a third distinct route to a more
    # precise mean, alongside `math.fsum` (compensated binary-float summation)
    # and `decimal.Decimal` (exact base-10 arithmetic) explored in prior
    # attempts on this task: this one stays exact by working in exact
    # rationals rather than in any fixed-radix floating-point representation.
    naive_mean = sum(values) / len(values)
    fraction_mean = statistics.mean(values)
    score = fraction_mean
    record = {
        "score": score,
        "metrics": {
            "n": len(values),
            "naive_mean": naive_mean,
            "means_agree": naive_mean == fraction_mean,
        },
        "notes": "",
    }
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
