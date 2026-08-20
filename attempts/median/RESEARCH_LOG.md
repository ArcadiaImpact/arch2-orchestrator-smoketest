# Research log — median instead of mean

## Idea

Research direction 3 in `findings/toysmoke2/problem.md` asks to swap the
arithmetic mean for the median and characterise where the two diverge.
The mean and the median only diverge when a distribution is skewed or
has outliers pulling the mean away from the central value; on a
symmetric, evenly-spaced sample they coincide exactly. Both the public
sample (`1, 2, 3, 4, 5`) and the held-out sample (`10, 20, 30`, per
`problem.md`) are small, symmetric, evenly-spaced sets, so this attempt
is a test of that prediction: does the median actually match the mean
on data built specifically not to distinguish estimators?

## What I did

Changed `eval.py` to report `statistics.median(values)` as `score`
instead of `sum(values) / len(values)`, and kept the mean around as
`metrics.mean_baseline` (an internal-only metric per
`[publish].public_metrics` in `.arch/config.toml`, not exposed on the PR
comment) so the two numbers can be compared from a single eval run
without needing to check out the direction-1 attempt (#9) separately.

## What I saw

On the public sample, `statistics.median([1,2,3,4,5]) = 3.0`, identical
to the mean. `arch eval` prints `score: 3.0`, matching the direction-1
baseline (PR #9) exactly on public data.

## What this does and doesn't tell us

This confirms the predicted non-divergence on this specific data: for
an odd-length, evenly-spaced, symmetric sample, mean and median are
mathematically guaranteed to be equal, not just empirically close. The
held-out sample (`10, 20, 30`) is the same shape (odd length, symmetric,
evenly spaced), so the median is expected to also equal the held-out
mean of 20.0 there. This attempt therefore cannot demonstrate a case
where median and mean actually disagree — per `problem.md`, no attempt
on this task's data can, since "the arithmetic mean, a trimmed mean, the
median, ... all return 20.0 on a three-row symmetric sample." The value
of running it anyway is confirming that expectation holds rather than
assuming it, and leaving `mean_baseline` in the metrics as a
ready-made comparison point for whoever looks at this PR later.

## Next steps

To actually see mean and median diverge, the sample itself would need
to be asymmetric (e.g. add an outlier). That's a change to the *data*,
not the estimator, and out of scope here since both `data/public` and
the held-out sample are fixed inputs to this smoke test, not something
an attempt should modify.
