# Does trimming the tails change the summary of a tabular sample?

## Problem

A CSV with a `value` column has to be reduced to a single number. The
obvious choice is the arithmetic mean, but the mean is maximally sensitive
to extreme values: one bad row moves it by an amount proportional to how
bad the row is. A trimmed mean is the standard defence — sort the values,
discard a fixed fraction from each tail, and average what remains. The
question here is whether that substitution actually changes the answer on
the data at hand, and therefore whether the robustness is being bought at
any cost in accuracy.

## Method

The reduction in `eval.py` computes a trimmed mean rather than a plain
average. `trimmed_mean()` sorts the values, computes `k = round(0.2 * n)`,
and averages the slice `values[k : n-k]`, falling back to the untrimmed list
when trimming would discard everything. The trim fraction of 0.2 — roughly
the top and bottom fifth — was fixed in advance as a conventional default
rather than tuned; the aim was to find out whether trimming matters at all,
not to search for the fraction that produces the most agreeable number.

The unmodified arithmetic mean is computed alongside it and recorded in the
output's `metrics` field, so the two statistics can be read off the same run
and compared directly instead of across separate runs.

## Result

The two statistics agree on both samples examined.

On the development sample (values 1 through 5), `k = 1`, so the extremes 1
and 5 are dropped and {2, 3, 4} is averaged, giving 3.0 — exactly the plain
arithmetic mean. On a separate evaluation sample not available during
development, the trimmed mean is 20.0, again matching the untrimmed mean
recorded on the same run.

The honest reading is that this comparison is uninformative rather than
supportive. Both samples are small and symmetric about their centre, and
trimming a symmetric set from both tails cannot move its mean — the
agreement is forced by the shape of the data, not evidence that trimming is
harmless in general. The evaluation sample is small enough that
`round(0.2 * n)` trims down to a single retained value, at which point the
statistic has collapsed into the median and is no longer a trimmed mean in
any meaningful sense. So the experiment establishes that trimming costs
nothing *here*, and nothing beyond that.

Notably, the result does not go the other way either: a plausible worry was
that discarding real observations would pull the estimate away from the true
mean. On these samples it does not, because there is no asymmetry for it to
expose.

## Limitations

The trim fraction was never varied, so the sensitivity of the result to that
choice is unmeasured. More fundamentally, the discriminating case — a skewed
sample, where the trimmed and untrimmed means genuinely diverge — was never
tested, because no such sample was available. Any claim about robustness to
outliers is therefore untested by this work. On samples of fewer than about
five rows the 20% rule degenerates, and the statistic should be read as a
median rather than a trimmed mean.

## Reproduction

```sh
ARCH_DATA_ROOT=data/public python eval.py
```

- Method: `eval.py` (`trimmed_mean`, `TRIM_FRACTION`)
- Notes: `attempts/trimmed-mean/`
- Development sample: `data/public/sample.csv`

The run writes `{score, metrics}` JSON to `$ARCH_EVAL_OUTPUT`; the
untrimmed comparison value is `metrics.arithmetic_mean`.
