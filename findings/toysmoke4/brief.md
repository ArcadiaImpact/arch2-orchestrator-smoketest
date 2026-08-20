# Compensated summation for the mean

## Problem

The arithmetic mean divides a sum of floating-point values by their count.
The built-in `sum()` adds left to right and accumulates one rounding error
per addition, because most decimal fractions (e.g. `0.1`) have no exact
binary floating-point representation. For long or ill-conditioned inputs
that accumulated error can perturb the mean. The question is whether
replacing the summation with a compensated algorithm removes that error
source without disturbing results that were already exact.

## Method

A single line in `eval.py` was changed: the sum feeding the mean now comes
from `math.fsum(values)` instead of `sum(values)`. `math.fsum` implements
the Shewchuk algorithm, which tracks the per-step rounding error and
corrects for it, returning a result correctly rounded to the true
mathematical sum. Both the plain and compensated sums, and their difference,
are retained in the run's metrics so the two paths can be compared directly.
Because this task's real inputs are already exact in binary float, a
standalone demonstration (`attempts/fsum-compensated-sum/demo_fsum_gap.py`)
exercises the mechanism on an input that is not — ten copies of `0.1`.

## Result

On the demonstration input `sum()` returns `0.9999999999999999` while
`math.fsum()` returns exactly `1.0`, making the corrected rounding error
concrete. On this task's actual data the change is a verified no-op: the
sample `[1, 2, 3, 4, 5]` and the validation sample `(10, 20, 30)` are small
integers with exact binary representations, so the plain-versus-compensated
difference is `0.0` and the mean is unchanged (`3.0` and `20.0`
respectively). The result is thus a correctness safeguard — compensated
summation where it matters, provably identical where it does not — rather
than a numeric change on the inputs at hand.

## Limitations

The benefit is unobservable on the fixed inputs here, all of which are
exactly representable; the improvement would only register on data
containing values with binary representation error (or on sums long enough
for left-to-right rounding to accumulate), which this task does not provide.

## Reproduction

- Method: the `math.fsum` summation in `eval.py`; mechanism demo in
  `attempts/fsum-compensated-sum/demo_fsum_gap.py`.
- Run: `python3 attempts/fsum-compensated-sum/demo_fsum_gap.py` and
  `python3 eval.py` (pure-stdlib Python, no dependencies or GPU).
