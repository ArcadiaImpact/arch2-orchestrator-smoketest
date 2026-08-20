"""Toy smoke-test eval: mean of values in sample.csv. Reads ARCH_DATA_ROOT."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path


def parse_values(f) -> tuple[list[float], int]:
    """Parse a 'value' column, skipping rows that aren't a usable number.

    Returns (values, skipped_count). A blank line, a missing 'value' cell,
    or a non-numeric cell is skipped rather than raising, so one bad row in
    an otherwise-good file doesn't take down the whole eval.
    """
    values: list[float] = []
    skipped = 0
    for row in csv.DictReader(f):
        raw = (row.get("value") or "").strip()
        if not raw:
            skipped += 1
            continue
        try:
            values.append(float(raw))
        except ValueError:
            skipped += 1
    return values, skipped


def main() -> int:
    data_root = Path(os.environ["ARCH_DATA_ROOT"])
    output_path = Path(os.environ["ARCH_EVAL_OUTPUT"])

    csv_path = data_root / "sample.csv"
    with csv_path.open() as f:
        values, skipped = parse_values(f)

    if not values:
        record = {"score": None, "metrics": {"n": 0, "skipped": skipped}, "notes": "no usable rows"}
        output_path.write_text(json.dumps(record))
        return 0

    score = sum(values) / len(values)
    record = {"score": score, "metrics": {"n": len(values), "skipped": skipped}, "notes": ""}
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
