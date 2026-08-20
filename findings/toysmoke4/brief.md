# Verifying the arithmetic mean of a numeric column

## Problem

The task is to compute a summary statistic — the arithmetic mean — of a
single numeric column read from a CSV file, and to be confident that the
computation is correct rather than merely plausible. The mean is the
reference against which every alternative estimator (trimmed mean, median,
compensated summation, exact decimal arithmetic) is judged, so its
correctness needs to be established as a checked fact, not assumed because
the one-line formula `sum(values) / len(values)` looks obviously right.

## Method

The evaluation reads the value column with `csv.DictReader` and returns
`sum(values) / len(values)`. Rather than trust that path by inspection, this
work adds an independent verifier (`attempts/mean-baseline/verify_baseline.py`)
that re-implements the mean on a separate code path and checks it two ways:
it asserts the parsed sample is exactly `[1.0, 2.0, 3.0, 4.0, 5.0]` — i.e.
that the input is what the problem statement says it is, not just "some
numbers" — and it asserts the computed mean equals a hand-derived expected
value of `(1 + 2 + 3 + 4 + 5) / 5 = 3.0`. Because the check compares against
a value derived by hand rather than against the evaluation re-run against
itself, a bug shared by both code paths would still be caught.

## Result

The arithmetic mean of the sample column is `3.0`, matching the hand-derived
expectation exactly; the verifier prints
`OK: arithmetic_mean([1.0, 2.0, 3.0, 4.0, 5.0]) == 3.0 == expected 3.0`.
Applied to a separate validation sample `(10, 20, 30)`, the same formula
returns `20.0`, again matching its hand-computed mean, so the computation
transfers to inputs it was not tuned on. This fixes the arithmetic mean as a
verified reference: subsequent estimators can claim to "match" or "diverge
from" it against a value that has itself been checked.

## Reproduction

- Method: `attempts/mean-baseline/verify_baseline.py` (independent verifier).
- Run: `python3 attempts/mean-baseline/verify_baseline.py` and `python3 eval.py`.
- Both are pure-stdlib Python and need no dependencies or GPU.
