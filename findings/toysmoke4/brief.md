# Median versus mean as the summary statistic

## Problem

Summarising a numeric column by its arithmetic mean is sensitive to
outliers and skew; the median is the natural robust alternative. The
question here is a characterisation one: for the data at hand, does swapping
the mean for the median change the reported value, and — more usefully —
under what conditions are the two estimators guaranteed to agree or to
diverge?

## Method

The estimator computed over the value column was changed from
`sum(values) / len(values)` to `statistics.median(values)` in `eval.py`,
with both quantities retained side by side in the run's metrics so they can
be compared directly on the same input. The sample column is `[1, 2, 3, 4, 5]`.

## Result

On this column the median is `3.0` — identical to the arithmetic mean. This
is not a coincidence to be explained away but the finding itself: for an
odd-length, symmetric list (values evenly spaced about a centre, here 1–5
about 3), the middle element *is* the arithmetic mean, so the two estimators
are mathematically forced to coincide. The same holds for the separate
validation sample `(10, 20, 30)`, which is likewise odd-length and
symmetric and yields `20.0` for both statistics. The concrete contribution
is therefore a boundary rather than a numeric gap: mean and median agree
exactly when the count is odd and the distribution is symmetric, and diverge
precisely when neither holds (even count, or skew/outliers). Neither sample
in this task exercises the second regime, so this particular data cannot
numerically distinguish the two estimators.

## Limitations

Because both available samples are odd-length and symmetric, the divergence
regime is characterised analytically but not demonstrated on data here.
Observing an actual mean/median gap would require an input with an even
count or an outlier — a change to the measured data, not to the method.

## Reproduction

- Method: the median computation in `eval.py`; reasoning in
  `attempts/median/RESEARCH_LOG.md`.
- Run: `python3 eval.py` (pure-stdlib Python, no dependencies or GPU).
