# Exact-rational mean of a CSV column

## Problem

The obvious way to average a column of numbers, `sum(values) / len(values)`,
does its arithmetic in binary floating-point. When the inputs cannot be
represented exactly in binary — decimal fractions such as 0.1 or 0.2 — each
addition can introduce a small rounding error, and those errors can accumulate
across a long sum. The question here is whether computing the mean in exact
arithmetic, so that no intermediate rounding occurs at all, gives a more
faithful result, and whether it agrees with the direct floating-point mean on
inputs where no rounding is possible.

## Method

Each value is read from the CSV and the mean is computed with the standard
library's `statistics.mean`. Unlike a direct sum, `statistics.mean` does not
add the floating-point values together. Internally it converts each value to an
exact rational (`fractions.Fraction`, with unbounded-precision numerator and
denominator, so the conversion captures the exact value the float already
holds), sums those rationals with no rounding at any step, divides exactly, and
converts back to a float only once, at the very end. This keeps the whole
computation exact regardless of the number base — a different route to
precision than staying in binary and merely stabilising the order of addition.

As an internal cross-check, the direct floating-point mean is computed
alongside it and the two are compared for exact equality.

## Result

On the sample dataset — five rows with the values 1 through 5 — the
exact-rational mean is **3.0**, and it agrees exactly with the direct
floating-point mean. This is the expected outcome: every value is an integer
with an exact binary representation, so there is no rounding for any method to
avoid, and the exact-rational route neither improves on nor regresses from the
direct sum. The method is confirmed to be a faithful drop-in for the direct
mean on well-behaved input.

## Limitations

Because the sample contains only integers, this experiment cannot exhibit the
advantage the exact-rational approach is meant to provide — a measurable
difference would only appear on inputs whose values lack exact short binary
representations (for example 0.1, 0.2, 0.3), where accumulated floating-point
error would make the direct sum diverge from the exact result. On such inputs
the exact-rational mean would be the more accurate of the two; that regime is
not exercised here.

## Reproduction

With the repository's sample data, run the eval and read the mean from its
output:

```
ARCH_DATA_ROOT=data/public ARCH_EVAL_OUTPUT=/tmp/out.json python eval.py
cat /tmp/out.json
```

The method lives in `eval.py`; supporting notes are in
`attempts/fraction-mean/RESEARCH_LOG.md`.
