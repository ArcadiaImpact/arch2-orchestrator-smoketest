# Robust CSV parsing — research log

## Direction

Direction 4 from the seeded hypothesis space: harden the reader so a
malformed, blank, or non-numeric row cannot crash the eval. Independent of
PR #22 (mean baseline) and PR #23 (median) — this attempt doesn't change
which statistic is computed, only how resilient the parsing is to bad rows
in the input file.

## What I did

The original `eval.py` does `[float(row["value"]) for row in
csv.DictReader(f)]`, which raises `ValueError` and crashes the whole eval
the moment any row's `value` cell is blank or non-numeric. I replaced this
with `parse_values()`, which iterates rows, treats a missing/blank cell or a
`ValueError` from `float()` as "skip this row" rather than a fatal error,
and returns both the usable values and a count of how many rows were
skipped. `eval.py` now also handles the degenerate case of zero usable rows
(reports `score: null` with a note instead of raising `ZeroDivisionError`).

To demonstrate this actually matters rather than asserting it, I added
`attempts/robust-csv/malformed_sample.csv` (a copy of the public sample with
an injected blank line and a `not_a_number` row) and
`attempts/robust-csv/demo_robustness.py`, which runs the *original*
one-line parser against that file (confirmed: raises `ValueError`) and the
patched `parse_values` against the same file (confirmed: returns `[1.0, 2.0,
4.0, 5.0]`, skips 1 row — `csv.DictReader` itself already drops fully-blank
lines before they reach application code, so only the non-numeric cell is
caught by the new skip logic — and computes the same mean, 3.0, as the clean
public sample).

## Why this doesn't change the score on the real data

`data/public/sample.csv` and (per `findings/toysmoke4/problem.md`) the
held-out sample are both clean — no blank or non-numeric rows — so this
change is a no-op on the actual scored files: `arch eval` still returns
`score: 3.0`, identical to PR #22's baseline. This matches what
`problem.md` says explicitly: "the 'robust CSV parsing' direction ... is
only meaningfully different from the baseline on malformed input, and the
held-out file is clean, so both score identically." The value of this
attempt is not a score change but a demonstrated behavior difference on
input the real files don't contain — the malformed-input demo is the actual
evidence, not the `arch eval` number.

## What I'd try next

The one thing this attempt doesn't cover: rows where the CSV header itself
is missing or renamed (e.g. `val` instead of `value`), which would currently
make every row's `row.get("value")` return `None` and skip everything,
landing on the `score: null` / "no usable rows" path. That's arguably correct
behavior (fail loudly with a null score rather than silently computing a
mean of nothing) but it's untested here and would be worth its own demo file
if this direction were pursued further.
