"""Toy smoke-test eval: mean of values in sample.csv. Reads ARCH_DATA_ROOT."""
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

    if not values:
        raise ValueError(f"no numeric rows found in {csv_path}")

    score = sum(values) / len(values)
    notes = f"skipped {skipped} malformed/blank row(s)" if skipped else ""
    record = {"score": score, "metrics": {"n": len(values), "skipped": skipped}, "notes": notes}
    output_path.write_text(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
