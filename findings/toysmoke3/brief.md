# Median as an alternative to the mean

## Problem

The arithmetic mean summarizes a column of numbers but is sensitive to every
value, so a single outlier shifts it. The median depends only on the central
value(s) of the sorted data and is insensitive to how far extreme values sit
from the center. This work reports the median in place of the mean and
characterizes where the two summaries diverge.

## Method

The values are parsed from the CSV and both statistics are computed: the mean as
`sum(values) / len(values)` and the median as `statistics.median(values)`. The
median is reported as the result, with the mean, the median, and their
difference retained for comparison. The two coincide when the data is symmetric
about its center and diverge under skew or an outlier.

## Result

On the reference sample (values 1 through 5) the mean and median are both 3.0 —
their difference is 0.0 — because the five values are evenly spaced and
symmetric about their middle element. On this dataset the median-based summary
is indistinguishable from the mean and matches the published reference value of
3.0. The two statistics would separate only on a skewed dataset or one
containing an outlier.

## Limitations

The reference data is symmetric by construction and therefore cannot distinguish
the median from the mean; a skewed or outlier-bearing sample would be needed to
observe the divergence this direction exists to characterize.

## Reproduction

Run the eval against the public data in the current revision of this repo. The
method lives in `attempts/median/`, with the computation in `eval.py`.
