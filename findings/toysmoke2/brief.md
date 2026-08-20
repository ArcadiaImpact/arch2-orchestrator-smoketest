# Hardening the CSV reader against malformed rows

## Problem

The task computes a summary statistic over a `value` column read from a
CSV file. The straightforward reader coerces every row with
`float(row["value"])` unconditionally, which means a single blank field, a
missing `value` column, or a non-numeric string raises an uncaught
exception and aborts the whole computation. For a pipeline that is
expected to return a well-formed result (or an explicit "no result")
rather than crash, that is a fragility worth removing: one bad row should
not take down an otherwise valid dataset.

## Method

The parsing loop is factored into a `load_values(csv_path)` helper that
tolerates malformed input instead of assuming clean input. A missing or
blank `value` field is treated as skippable rather than raising; a
non-numeric string that fails `float()` is caught and the row skipped; and
the helper returns both the surviving numeric values and a count of
skipped rows. The caller reports that skip count and, if every row turns
out unusable, returns an explicit null result with a note instead of
dividing by zero. The estimator itself is unchanged — the surviving values
are still averaged the same way — so the hardening is purely at the
input-handling layer. A small fixture
(`attempts/robust-parsing/malformed_fixture.csv`, containing a blank field
and a non-numeric entry among valid rows) and a demo
(`attempts/robust-parsing/demo_malformed.py`) exercise the helper directly.

## Result

On the malformed fixture, `load_values` returns the five valid numbers and
reports one skipped row, having discarded the non-numeric entry without
raising. On clean input the change is a no-op: the sample dataset
(`1, 2, 3, 4, 5`) still averages to `3.0`, exactly as before — robustness
should not perturb the answer on well-formed data, and it does not. One
detail worth recording: `csv.DictReader` already drops fully blank
*lines* internally before they reach the loop, so a blank line never
reaches the skip counter; only a row with a present-but-invalid field is
counted.

## Limitations

The hardening is defensive against inputs the current dataset does not
contain, so it cannot change the computed summary on the data at hand. Its
value is that the reader now fails gracefully on inputs it was previously
untested against, not that it improves any result on well-formed input.

## Reproduction

From the current revision of this repository:

```sh
python3 attempts/robust-parsing/demo_malformed.py   # exercises the hardened reader
python3 eval.py                                      # unchanged result on clean data
```

The hardened reader lives in `eval.py` (`load_values`); the fixture and
demo are under `attempts/robust-parsing/`.
