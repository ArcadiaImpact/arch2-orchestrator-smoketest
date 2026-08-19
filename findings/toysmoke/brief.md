# An order statistic in place of an average: median versus mean

## Problem

Reducing a column of numbers to a single summary usually means taking the
arithmetic mean. The mean uses the magnitude of every observation, which is
what makes it efficient and also what makes it fragile: a single extreme
value shifts it. The median takes the opposite position — it uses only the
ordering of the observations and, for an odd number of rows, reports one of
them verbatim, discarding every other value's magnitude entirely. The
question addressed here is whether that difference in mechanism produces a
difference in answer on the data in question.

This is a sharper question than it may appear. Trimming the tails of a
sample and taking its median are often lumped together as "robust"
alternatives to the mean, but they are not variants of one idea: a trimmed
mean still averages a subset of the data, whereas the median averages
nothing at all. The two can agree or disagree independently of each other.

## Method

The reduction in `eval.py` computes the median of the `value` column instead
of its mean: the values are sorted and the middle one is taken, with the two
central values averaged when the row count is even. Both samples used here
have an odd row count, so in practice the reported figure is a single
observation drawn unchanged from the data.

The arithmetic mean is still computed on the same pass and recorded in the
output's `metrics` field as `arithmetic_mean`, so the two summaries are
produced from identical inputs in a single run and can be compared without
re-reading the file.

## Result

The median and the mean coincide on both samples examined.

On the development sample (values 1 through 5) the median is 3, matching the
mean of 3.0 exactly. On a separate evaluation sample not available during
development, the median is 20.0, again equal to the mean computed on the
same run.

The interesting part is what the agreement implies about the data rather
than about the estimator. A median equal to the mean is a statement that the
sample is balanced about its centre — the observations above the middle
value offset those below it. On the development sample this is visible by
inspection: 1, 2, 3, 4, 5 is symmetric by construction. That it also holds on
the evaluation sample says the same symmetry is present there, which was not
knowable in advance.

Consequently this experiment cannot separate the two estimators. It rules
out the possibility that switching to an order statistic silently changes
the answer on this data, and it establishes symmetry as a property of both
samples, but it provides no evidence about which summary to prefer when the
data is skewed — the only regime in which the choice has consequences.

## Limitations

Only odd-row samples were used, so the even-`n` path, which averages the two
central observations and is therefore not a pure order statistic, is
untested. The samples are very small — a handful of rows each — so the
observed symmetry may be incidental rather than a stable property of the
data source. No skewed sample was available, which leaves the central
question of the comparison open.

## Reproduction

```sh
ARCH_DATA_ROOT=data/public python eval.py
```

- Method: `eval.py`
- Notes: `attempts/median/`
- Development sample: `data/public/sample.csv`

The run writes `{score, metrics}` JSON to `$ARCH_EVAL_OUTPUT`; the mean used
for comparison is `metrics.arithmetic_mean`.
