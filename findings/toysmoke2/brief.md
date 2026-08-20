# Median versus arithmetic mean on symmetric data

## Problem

A common robustness question for a summary statistic is whether reporting
the median instead of the arithmetic mean changes the answer. The mean and
the median only diverge when the distribution is skewed or dragged by
outliers; on a symmetric, evenly spaced sample they coincide exactly. The
task here computes a summary of a column of numbers from a CSV, and this
attempt asks a concrete version of that question: on data that was
deliberately built to be simple and symmetric, does switching from the
mean to the median move the reported value at all?

## Method

The reported statistic is changed from `sum(values) / len(values)` to
`statistics.median(values)`. The arithmetic mean is retained alongside it
as an internal `mean_baseline` metric, so that both numbers are produced
by a single run and the mean/median comparison can be read directly from
one evaluation rather than by cross-referencing a separate baseline run.

## Result

On the sample dataset (`1, 2, 3, 4, 5`) the median is `3.0`, identical to
the arithmetic mean. This is not a coincidence to be measured but a
mathematical guarantee: for an odd-length, evenly spaced, symmetric set,
the middle value equals the mean exactly. The reported summary is
therefore unchanged by the substitution, confirming the predicted
non-divergence rather than merely observing that the two happen to be
close.

## Limitations

The finding is exactly as strong as the data allows: because the sample is
symmetric, this attempt cannot exhibit a case where the median and mean
actually disagree. Demonstrating divergence would require an asymmetric
sample (for instance, one containing an outlier), which is a change to the
input data rather than to the estimator and is out of scope for a
comparison of estimators on a fixed dataset.

## Reproduction

From the current revision of this repository, with `ARCH_DATA_ROOT`
pointing at the sample data directory:

```sh
python3 eval.py
```

The estimator change lives in `eval.py`; the reasoning is recorded in
`attempts/median/RESEARCH_LOG.md`.
