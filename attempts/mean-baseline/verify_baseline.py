"""Independent check for direction 1 (arithmetic mean baseline).

Re-implements the mean computation from eval.py in isolation (no CSV
parsing, no ARCH_DATA_ROOT) and checks it against a hand-computed
expected value for the public sample (1, 2, 3, 4, 5). This is a second,
independent code path — not a re-run of eval.py — so agreement here is
evidence the formula itself is right, not just that eval.py didn't crash.

Run: python3 attempts/mean-baseline/verify_baseline.py
"""
from __future__ import annotations

import csv
from pathlib import Path

PUBLIC_CSV = Path(__file__).resolve().parents[2] / "data" / "public" / "sample.csv"


def arithmetic_mean(values: list[float]) -> float:
    return sum(values) / len(values)


def main() -> None:
    with PUBLIC_CSV.open() as f:
        values = [float(row["value"]) for row in csv.DictReader(f)]

    computed = arithmetic_mean(values)
    expected = 3.0  # (1 + 2 + 3 + 4 + 5) / 5, per findings/toysmoke4/problem.md

    assert values == [1.0, 2.0, 3.0, 4.0, 5.0], f"unexpected public sample: {values}"
    assert computed == expected, f"baseline mismatch: got {computed}, expected {expected}"

    print(f"OK: arithmetic_mean({values}) == {computed} == expected {expected}")


if __name__ == "__main__":
    main()
