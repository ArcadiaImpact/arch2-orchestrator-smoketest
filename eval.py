"""Toy smoke-test eval: arithmetic mean of values in sample.csv, made
tolerant of malformed rows (attempt `robust-parse`).

problem.md's two seeded directions are both about which *statistic* to
compute (plain mean vs. a trimmed/robust mean). Prior attempts on this task
(PR #2: plain arithmetic mean, PR #3: trimmed mean, PR #4: median) all
answered that question and, per each attempt's own research log, converged
on "no statistic beats the plain arithmetic mean, because the task's target
is definitionally the arithmetic mean of the held-out data." PR #4's log
explicitly flags the next open question as *not* another statistic, but
whether the baseline computation itself is robust to malformed input rows
(blank lines, non-numeric values) -- something none of the prior attempts
touched, since `data/public/sample.csv` happens to contain only clean rows.

This attempt tests that: it keeps the arithmetic mean as the statistic
(direction 1, unchanged) but changes *parsing* so a blank row or a
non-numeric `value` cell is skipped with a count, instead of the whole eval
crashing with an uncaught ValueError (the original baseline's behavior,
inherited from `float(row["value"])` with no guard). This matters because a
CSV-parsing crash produces a `null` score, which `arch findings` and the
held-out pipeline can't distinguish from "still running" (see problem.md,
"Two specific misreadings to guard against") -- a fragile parser silently
converts a data-quality issue into a false "pod died" signal.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path


def main() -> int:
    data_root = Path(os.environ["ARCH_DATA_ROOT"])
    output_path = Path(os.environ["ARCH_EVAL_OUTPUT"])

    csv_path = data_root / "sample.csv"
    values: list[float] = []
    skipped = 0
    with csv_path.open() as f:
        for row in csv.DictReader(f):
            raw = (row.get("value") or "").strip()
            if not raw:
                skipped += 1
                continue
            try:
                values.append(float(raw))
            except ValueError:
                skipped += 1

    score = sum(values) / len(values)
    record = {
        "score": score,
        "metrics": {"n": len(values), "skipped": skipped},
        "notes": "robust-parse",
    }
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
