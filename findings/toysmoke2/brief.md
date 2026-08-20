# Verifying the arithmetic-mean reference

## Problem

The task is to compute the arithmetic mean of a column of numbers read
from a CSV file. Because every other estimator considered here (a trimmed
mean, the median, a robustness-hardened parser, compensated summation,
exact decimal arithmetic) is only meaningful relative to that arithmetic
mean, the mean is the reference the whole comparison rests on. Before
building anything on top of it, it is worth establishing that the
reference computation is itself correct — a silent bug in the baseline
(an off-by-one in the count, a float-accumulation error) would quietly
corrupt every downstream comparison.

## Method

Rather than reimplement the mean, this attempt checks the existing
computation. The estimator under test is the direct
`sum(values) / len(values)`. A small standalone script,
`attempts/mean-baseline/verify_mean.py`, loads the `value` column and
recomputes the mean a second, independent way — Python's standard-library
`statistics.mean`, which accumulates over exact fractions rather than raw
floating-point division, so it exercises a genuinely different code path.
The script asserts the two results agree and prints both. The scoring code
itself is deliberately left unchanged; the goal is to validate the
reference, not to replace it.

## Result

On the sample dataset (`1, 2, 3, 4, 5`) both computations return exactly
`3.0`, in agreement, confirming the arithmetic mean is computed correctly
end to end from the CSV through to the reported value. Two independent
algorithms agreeing to the bit rules out the most likely silent failures
in the baseline.

## Limitations

This is a consistency check between two correct-by-construction
implementations on clean, symmetric data; it cannot surface a case where
`sum/len` and fraction-based accumulation would diverge, because such a
divergence needs numerically adversarial inputs this dataset does not
contain. Its guarantee is therefore narrow — the reference is correct on
the data at hand — rather than a general robustness claim.

## Reproduction

From the current revision of this repository:

```sh
python3 attempts/mean-baseline/verify_mean.py
```

The method lives entirely in `attempts/mean-baseline/verify_mean.py`.
