# Research log — robust CSV parsing

## Idea

Research direction 4 asks to harden the CSV reader so a malformed,
blank, or non-numeric row can't crash the eval. The original `eval.py`
does `float(row["value"])` unconditionally for every row: a blank line,
a row where `value` is empty, or a row with a non-numeric string all
raise an uncaught exception, which per `.arch/eval.sh`'s output contract
would surface as a crash rather than a clean `null` score.

## What I did

Refactored the parsing loop in `eval.py` into `load_values(csv_path)`,
which now:

- treats a missing or blank `value` field as skippable rather than
  raising `KeyError`/`ValueError`,
- catches `ValueError` from `float()` on a non-numeric string and skips
  that row instead of propagating the exception,
- returns both the surviving numeric values and a count of skipped rows.

`main()` now reports `skipped` in `metrics`, and — if every row turned
out to be unusable — returns `score: null` with a note instead of
dividing by zero.

Added `attempts/robust-parsing/malformed_fixture.csv` (values `1, 2,
<blank>, not_a_number, 3, 4, 5`) and
`attempts/robust-parsing/demo_malformed.py`, which imports `load_values`
directly from `eval.py` and asserts it returns `[1.0, 2.0, 3.0, 4.0,
5.0]` with `skipped == 1` on that fixture, run independently of `arch
eval` so it doesn't touch `data/public/sample.csv`.

## What I saw

`python3 attempts/robust-parsing/demo_malformed.py` printed
`values=[1.0, 2.0, 3.0, 4.0, 5.0] skipped=1` and passed both assertions.
One nuance found while writing this: `csv.DictReader` already silently
skips fully-blank *lines* before they reach the per-row loop (it treats
a blank line as `row == []` and skips it internally), so only the
non-numeric row (`not_a_number`) was counted by our own `skipped`
counter — the blank line never reached our `try`/`except` at all. The
log in the demo script documents this so the count isn't mysterious.

On `data/public/sample.csv` (which has no malformed rows), `arch eval`
still returns `score: 3.0`, matching the direction-1 baseline (PR #9)
exactly — the hardening is a no-op on clean data, which is the
behavior we want: robustness should not change the answer on
well-formed input.

## What this does and doesn't tell us

This attempt doesn't change the *estimator* (still `sum/len`, same as
the baseline) — it changes what happens on inputs the current public
and held-out samples don't contain. Since both samples are known-clean,
this attempt can't move the score on either; its value is defensive
(the eval no longer crashes on a row it wasn't shown here), not
score-affecting to the task's own data.

## Next steps

None planned — this is a narrow hardening pass, not a method with
further iterations. A natural follow-up would be combining this with
another direction (e.g. compensated summation) to hardening a
non-baseline estimator too, but that would be a distinct attempt.
