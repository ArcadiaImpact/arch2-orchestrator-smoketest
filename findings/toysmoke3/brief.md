# Compensated summation for the mean

## Problem

Computing the arithmetic mean of a list of floating-point values requires
summing them, and ordinary left-to-right summation rounds at every intermediate
step. For long sequences of similar-magnitude values that rounding can
accumulate into a visible error. The question is whether replacing the summation
with a compensated algorithm changes the computed mean, and by how much, on the
reference data.

## Method

The mean is computed as `math.fsum(values) / len(values)` instead of
`sum(values) / len(values)`. `math.fsum` (Shewchuk's algorithm) tracks partial
sums at full precision and rounds only once at the end, so it is immune to the
accumulation of intermediate rounding error. Both the naive and compensated
sums, and their difference, are recorded alongside the result so any divergence
between the two is directly visible.

## Result

On the reference sample (values 1 through 5) the compensated and naive sums are
identical — their difference is exactly 0.0 — and the mean is 3.0, matching the
published reference value. This is the expected outcome: a handful of small
integers has no intermediate rounding error to correct. The two summation
strategies diverge only when summing many terms, or terms of widely different
magnitudes, neither of which this dataset contains.

## Limitations

Because the reference data cannot exhibit floating-point accumulation error,
this dataset cannot demonstrate the benefit of compensated summation; it only
confirms that adopting it does not perturb the result on well-conditioned input.

## Reproduction

Run the eval against the public data in the current revision of this repo. The
method lives in `attempts/fsum-mean/`, with the summation change in `eval.py`.
