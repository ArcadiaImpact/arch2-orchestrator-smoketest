"""Toy smoke-test eval: arithmetic mean of values in sample.csv (attempt
`precise-sum`).

Keeps the statistic from PR #2 (the plain arithmetic mean) and PR #5
(tolerant CSV parsing) exactly as-is -- this attempt is not about which
statistic to compute or which rows to admit. It targets a different part of
the same computation: how the sum itself is accumulated before dividing by
`len(values)`.

`.arch/eval.sh`'s own header carries a documented numerical-precision
warning: "Python addition gives 5.000000000000004 from arithmetically-clean
inputs and silently fails the gate. Always: round(value, 2) before the gate,
and round again before serializing to JSON." That warning is written for
threshold *gates*, but the same mechanism -- naive left-to-right float
summation accumulating rounding error -- applies to any `sum()` over floats,
including the one this eval already does. `data/public/sample.csv` (1..5)
happens to sum exactly in binary floating point, so the bug this attempt
guards against is invisible on the public data; it would only show up on a
held-out CSV with values that don't happen to sum cleanly (e.g. repeating
binary fractions like 0.1, 0.2, 0.3).

This attempt swaps the built-in `sum()` for `math.fsum()`, which uses
compensated (Neumaier/Shewchuk) summation to track and correct for
accumulated rounding error, giving a correctly-rounded result regardless of
summation order. It also rounds the final score to 10 decimal places before
serializing, per the eval.sh guidance, so that any residual float-repr noise
(e.g. `3.0000000000000004`) doesn't leak into the JSON output. Neither
change alters which value is "correct" -- both should be identical to the
naive computation whenever the naive computation isn't already lossy, and
strictly closer to the true mean when it is.
"""
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

    score = round(math.fsum(values) / len(values), 10)
    record = {"score": score, "metrics": {"n": len(values)}, "notes": "precise-sum"}
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
