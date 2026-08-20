# Trimmed mean for outlier resistance

## Problem

The arithmetic mean of a column of numbers moves in proportion to any single
extreme value, so one corrupted or outlying row shifts the reported average. A
trimmed mean — dropping the most extreme values before averaging — is a standard
way to make the summary less sensitive to such outliers. This work computes a
trimmed mean and compares it against the plain arithmetic mean.

## Method

The parsed values are sorted and the single smallest and single largest are
dropped (`sorted(values)[1:-1]`); the mean of the remainder is reported. The
untrimmed mean is also computed for comparison. When fewer than three values are
present there is nothing left after trimming both ends, so the method falls back
to the untrimmed mean over all values.

## Result

On the reference sample (values 1 through 5), trimming removes the 1 and the 5,
leaving 2, 3, 4, whose mean is 3.0 — identical to the untrimmed mean and to the
published reference value. This is expected: trimming a symmetric distribution
removes equal mass from each side and does not shift the average. Here, "the
summary did not move" is itself the finding, and it reflects a property of the
data rather than an absence of effect in the method.

## Limitations

The reference data is symmetric with no outliers, so it cannot demonstrate where
the trimmed and plain means diverge; an asymmetric sample, or one containing an
outlier, would be required to exercise that difference.

## Reproduction

Run the eval against the public data in the current revision of this repo. The
method lives in `attempts/trimmed-mean/`, with the computation in `eval.py`.
