"""Toy smoke-test eval: mean of values in sample.csv. Reads ARCH_DATA_ROOT.

Parses defensively: a blank row, a row missing the `value` field, or a
row whose `value` isn't a number is skipped and counted rather than
crashing the eval (see attempts/robust-parsing/RESEARCH_LOG.md).
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path


def load_values(csv_path: Path) -> tuple[list[float], int]:
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
    return values, skipped


def main() -> int:
    data_root = Path(os.environ["ARCH_DATA_ROOT"])
    output_path = Path(os.environ["ARCH_EVAL_OUTPUT"])

    csv_path = data_root / "sample.csv"
    values, skipped = load_values(csv_path)

    if not values:
        record = {"score": None, "metrics": {"n": 0, "skipped": skipped}, "notes": "no numeric rows found"}
        output_path.write_text(json.dumps(record))
        return 0

    score = sum(values) / len(values)
    record = {"score": score, "metrics": {"n": len(values), "skipped": skipped}, "notes": ""}
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
