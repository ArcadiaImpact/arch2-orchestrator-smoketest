# Does compensated summation improve a floating-point column mean?

## Problem

Averaging a column of floating-point numbers requires summing them, and
naive left-to-right summation is the textbook example of accumulating
rounding error: each partial sum is rounded to the nearest representable
double, and those roundings compound. The standard remedy is compensated
summation — Kahan's algorithm and its Neumaier and Shewchuk refinements —
which tracks the discarded low-order bits and folds them back in, yielding a
correctly-rounded total independent of the order of accumulation.

The question addressed here is whether replacing the built-in summation with
an explicitly compensated one measurably improves the computed mean, and
whether the naive version is exposed to error the compensated version is
not.

## Method

The statistic and the parsing are unchanged; only the accumulation differs.
The mean is computed as `math.fsum(values) / len(values)`, where
`math.fsum` performs exact compensated summation, in place of the built-in
`sum`. The result is then rounded to ten decimal places before being
serialised, on the reasoning that any residual low-order noise in the float
representation should not leak into the output.

To test the premise rather than assume it, the two summation strategies were
compared directly against each other on the same inputs, rather than only
observing the final figure.

## Result

The change makes no difference to the computed mean, and the reasoning that
motivated it turns out not to apply to this implementation.

On the development sample the mean is 3.0 and on a separate evaluation
sample not available during development it is 20.0 — in both cases identical
to the naive computation. That much was expected: both samples are small
sets of values that sum exactly in binary floating point, so neither can
exercise the failure mode.

The substantive finding came from trying to exhibit the failure mode
deliberately. Across two thousand randomly generated samples of fifty values
spanning six orders of magnitude, the naive and compensated means were
bit-identical in every single case. Constructed adversarial inputs —
catastrophic cancellation between values of magnitude 10^16, and a large
value swamping a hundred small ones — also produced identical results. The
specific example used to motivate the change, the mean of ten copies of 0.1
and one 0.3, likewise gives exactly the same double either way.

The explanation is that the premise is out of date rather than wrong in
principle. Since version 3.12, CPython's built-in `sum` itself uses Neumaier
compensated summation when its arguments are floats. The baseline was
therefore already performing compensated summation, and `math.fsum`
substitutes one compensated algorithm for another. On the interpreter used
here (3.12), the change is a no-op by construction, not by luck.

The rounding step is worth separating out, because it does not share that
neutrality. Rounding to ten decimal places is a lossy operation applied
unconditionally: for the ten-copies-of-0.1 case it perturbs the result by
about 1.8 × 10^-11, which is roughly five orders of magnitude larger than
the double-precision representation error it was intended to suppress. On
this evidence the rounding degrades accuracy slightly rather than improving
it, and its justification — tidier serialised output — is presentational
rather than numerical.

## Limitations

The conclusion is interpreter-dependent in a way that matters. On CPython
before 3.12, or on an implementation whose `sum` is not compensated, the
substitution would be a genuine improvement rather than a no-op, and the
comparison reported here would come out differently. It also remains true
that `math.fsum` is exactly correctly-rounded whereas Neumaier summation is
merely very accurate, so inputs on which they diverge must exist; none was
found by random search or by the adversarial constructions tried, which
bounds how common such inputs are without establishing that there are none.

## Reproduction

```sh
ARCH_DATA_ROOT=data/public python eval.py
```

- Method: `eval.py`
- Notes: `attempts/precise-sum/`
- Development sample: `data/public/sample.csv`

To reproduce the comparison, evaluate `sum(v) / len(v)` against
`math.fsum(v) / len(v)` on the same list and check for bitwise equality; on
Python 3.12 and later they agree on all inputs tried.
