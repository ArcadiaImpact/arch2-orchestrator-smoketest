"""Toy smoke-test eval: mean of values in sample.csv (attempt `decimal-mean`).

Keeps the statistic from PR #2 (the plain arithmetic mean) unchanged -- this
attempt is not about which statistic to compute, it's about how the values
are represented while computing it.

PR #6 fixed one source of floating-point error: naive `sum()` accumulates
left-to-right rounding error, so it replaced `sum()` with `math.fsum()`
(compensated summation, correctly rounded regardless of order). But
`math.fsum()` still operates on the *binary floats* produced by `float(row)`
for each CSV value -- and that conversion itself already threw away
precision before summation ever starts. Most decimal fractions (0.1, 0.2,
0.3, ...) have no exact binary representation, so `float("0.1")` is already
an approximation of 0.1, and no amount of careful summation afterwards can
recover the digits that step discarded.

This attempt removes that error source instead of compensating for it
downstream: it parses each CSV value directly into a `decimal.Decimal` from
its original string, which preserves the exact decimal digits as written.
Summing and dividing `Decimal`s carries that exact value through the whole
computation, so there is exactly one rounding step in the entire pipeline --
converting the final `Decimal` mean to a `float` for JSON serialization --
versus one rounding-per-value at parse time plus (with the fsum fix) a
correctly-rounded-but-still-lossy division under the `float` approach.

Concretely: for values ['0.76','0.42','0.26','0.51','0.4','0.78','0.3'],
`math.fsum([float(v) for v in values]) / 7` gives
`0.49000000000000005`, while `float(sum(Decimal(v) for v in values) / 7)`
gives the more accurate `0.49`. `data/public/sample.csv` (integers 1..5)
can't exercise this -- integers have exact binary and decimal
representations either way -- so, like PR #6, this is only visible on a
held-out file with fractional values that don't sum or divide cleanly in
binary.
"""
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

    values = [Decimal(v) for v in raw_values]
    mean = sum(values) / len(values)
    score = float(mean)
    record = {"score": score, "metrics": {"n": len(values)}, "notes": "decimal-mean"}
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
