# Robust parsing of a numeric CSV column

## Problem

Computing the mean of a value column is only as reliable as the parser that
feeds it. The straightforward reader,
`[float(row["value"]) for row in csv.DictReader(f)]`, raises `ValueError`
and aborts on the first blank or non-numeric cell, so a single corrupted
row — a stray blank line, a placeholder string, a truncated upload — takes
down the entire computation. The question is whether the reader can be
hardened to tolerate individual bad rows without changing its answer on
clean input.

## Method

The parser was replaced by `parse_values()`, which treats a missing/blank
cell or a failed `float()` conversion as "skip this row and keep going,"
returning both the usable values and a count of skipped rows. When every
row is unusable the eval now reports no score with an explanatory note
rather than raising `ZeroDivisionError`. To make the behaviour observable —
clean input alone cannot distinguish the old and new readers — the work
includes a malformed fixture (`attempts/robust-csv/malformed_sample.csv`:
the sample with an injected blank line and a `not_a_number` row) and a
head-to-head harness (`demo_robustness.py`) that runs the original and
patched parsers against it.

## Result

On the malformed fixture the original parser crashes with `ValueError`, as
expected, while the hardened parser recovers the numeric rows
`[1.0, 2.0, 4.0, 5.0]`, reports one skipped row, and returns their mean of
`3.0`. Notably only one row reaches the skip logic: `csv.DictReader` drops
fully-blank lines itself, so the blank line never yields a row and only the
non-numeric cell is explicitly skipped. On clean input the reader is a
no-op relative to the original — the sample column still means `3.0` and the
validation sample `(10, 20, 30)` still means `20.0` — so robustness is
gained without altering the answer where the answer was already correct.

## Limitations

A structurally broken file — for example a renamed or missing `value`
header — causes every row to be skipped and the eval to report no score.
That is arguably the correct failure (average nothing loudly rather than
silently), but it is a fail-closed behaviour rather than a recovery, and is
not exercised by the fixture here.

## Reproduction

- Method: `parse_values()` in `eval.py`; demonstration in
  `attempts/robust-csv/demo_robustness.py` against
  `attempts/robust-csv/malformed_sample.csv`.
- Run: `python3 attempts/robust-csv/demo_robustness.py` and `python3 eval.py`
  (pure-stdlib Python, no dependencies or GPU).
