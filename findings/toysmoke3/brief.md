# Arithmetic-mean baseline

## Problem

The task is to compute the arithmetic mean of a column of numeric values from a
CSV. Before considering any robustness or precision variation, it is worth
pinning down the direct computation itself as an explicit, verifiable reference
against which every variation can be compared.

## Method

The values are read from the CSV with `csv.DictReader`, each `value` cell is
converted with `float()`, and the mean is computed directly as
`sum(values) / len(values)`. No parsing hardening, alternate summation, or
alternate statistic is applied — the computation is deliberately the plain,
unmodified reference.

## Result

On the reference sample (values 1 through 5) the computation returns a mean of
3.0, matching the published reference value exactly. This establishes the
baseline that the parsing, summation, and statistic variations are each measured
against.

## Reproduction

Run the eval against the public data in the current revision of this repo. The
baseline computation lives in `eval.py`, documented under
`attempts/arithmetic-baseline/`.
