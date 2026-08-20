"""Demonstrates direction 4 (robust CSV parsing) against a malformed file.

`malformed_sample.csv` in this directory has a blank line and a
non-numeric cell mixed into otherwise-valid rows (1, 2, blank,
not_a_number, 4, 5). The original `eval.py` (`float(row["value"])` with
no guard) raises `ValueError` on the blank/non-numeric rows and crashes
the whole eval. The patched `parse_values` in this attempt's `eval.py`
skips those rows and still returns a usable mean over the numeric ones.

Run: python3 attempts/robust-csv/demo_robustness.py
"""
from __future__ import annotations

import csv
from pathlib import Path

MALFORMED_CSV = Path(__file__).resolve().parent / "malformed_sample.csv"


def original_parse(f) -> list[float]:
    return [float(row["value"]) for row in csv.DictReader(f)]


def patched_parse(f) -> tuple[list[float], int]:
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


def main() -> None:
    with MALFORMED_CSV.open() as f:
        try:
            original_parse(f)
            raise AssertionError("expected the original parser to raise on malformed input")
        except ValueError as e:
            print(f"original parser: crashes as expected -> ValueError: {e}")

    with MALFORMED_CSV.open() as f:
        values, skipped = patched_parse(f)
    mean = sum(values) / len(values)
    print(f"patched parser: values={values} skipped={skipped} mean={mean}")
    assert values == [1.0, 2.0, 4.0, 5.0]
    # csv.DictReader silently drops fully-blank lines itself (no row is
    # yielded at all), so only the non-numeric cell reaches our skip path.
    assert skipped == 1
    assert mean == 3.0


if __name__ == "__main__":
    main()
