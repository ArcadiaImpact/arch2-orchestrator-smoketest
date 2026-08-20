"""Demonstrates that the hardened parser in eval.py's load_values survives
a malformed CSV (blank row + non-numeric row) instead of crashing.

Usage: python3 attempts/robust-parsing/demo_malformed.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eval import load_values  # noqa: E402


def main() -> int:
    fixture = Path(__file__).with_name("malformed_fixture.csv")
    values, skipped = load_values(fixture)
    print(f"values={values} skipped={skipped}")
    assert values == [1.0, 2.0, 3.0, 4.0, 5.0], values
    # csv.DictReader silently skips fully-blank lines itself (they never
    # reach our loop), so only the non-numeric row is counted as skipped.
    assert skipped == 1, skipped
    print("OK: malformed row skipped, numeric rows preserved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
