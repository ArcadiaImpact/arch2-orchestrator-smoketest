# Decimal-arithmetic mean — research log

## Starting point

The baseline eval (`eval.py` before this attempt) parses each CSV `value`
cell with `float(...)` and computes the mean as `sum(values) / len(values)`
using Python's binary-float arithmetic. This attempt implements seeded
direction #6 from `findings/toysmoke3/problem.md`: compute the mean with
`decimal.Decimal` instead, and compare the two results.

I checked the leaderboard (`arch findings --state all`) before starting.
Another worker had already opened PRs covering directions #1 (arithmetic
baseline), #2 (trimmed mean), #3 (median), #4 (robust CSV parsing), and #5
(compensated summation via `math.fsum`) — all scored 20.0 on held-out. This
attempt fills the one remaining seeded direction, #6, rather than
duplicating any of those.

## Why binary float vs. Decimal could diverge here

`float` represents numbers in base 2, so decimal fractions that terminate
cleanly in base 10 (like `0.1`) can't be represented exactly and pick up a
small representation error before any arithmetic happens. Summing several
such values can accumulate that error into something visible in the result.
`decimal.Decimal`, constructed directly from the CSV string (not from a
`float`), keeps the exact base-10 value, so summing and dividing stays exact
as long as the precision context is high enough — which it is by default
for a 3-row CSV.

## What I changed

In `eval.py`:
- Read each `value` cell as a raw string (`row["value"]`) instead of
  immediately coercing to `float`.
- Build `decimal_values = [Decimal(v) for v in raw_values]` and compute
  `decimal_mean = sum(decimal_values) / Decimal(len(decimal_values))`.
- Kept a `float_mean` computed the same way as the arithmetic-mean baseline,
  purely as an internal cross-check — not used for the reported score.
- The reported `score` is `float(decimal_mean)` (JSON has no native decimal
  type, so it has to be serialized as a float or a string; the task's
  output contract requires a numeric `score`, so `float` was used here).
- Added `decimal_mean` (as a string, to keep full precision visible),
  `float_mean`, and `decimal_float_agree` (whether the two methods produced
  bit-identical results) to `metrics` for internal inspection. Per
  `.arch/config.toml`'s public-metrics allow-list, none of these extra keys
  are surfaced on the PR — only `score` is.

## Local result

Public data (`data/public/sample.csv`, values `1,2,3,4,5`): `arch eval`
reports `score: 3.0`, matching the arithmetic baseline exactly, as expected
— integers have no binary-float representation error to begin with, so this
public sample can't exercise the divergence this attempt is actually testing
for. The `metrics.decimal_float_agree` field (visible only in the local run,
not on the PR) confirmed `decimal_mean == Decimal(float_mean)` for this input.

## What I'd try next

The public sample is all integers, so it cannot show any float/Decimal
divergence — a follow-up worth doing (as a *separate* attempt, not a push to
this PR) would add a public fixture CSV with non-terminating-binary
fractions (e.g. `0.1, 0.2, 0.3`) specifically to make the two methods
disagree and quantify the gap. I did not do that here because changing the
public fixture is a distinct hypothesis from "does Decimal arithmetic work
end-to-end," and mixing the two would make this attempt's diff harder to
read for the reasons stated in `problem.md`'s "why this measurement makes
sense" section — the score itself carries no research signal on this task,
only pipeline-health signal, so keeping the diff minimal and legible matters
more here than it would on a real research task.
