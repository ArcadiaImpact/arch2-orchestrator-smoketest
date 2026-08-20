# Trimmed mean — research log

## Idea

`problem.md` and the README seed a "trimmed mean" direction: drop the extreme
values from the sample before averaging, and compare against the arithmetic
mean baseline (see the baseline attempt in PR #16 / `attempts/arithmetic-baseline`).
A trimmed mean is a standard way to make an average less sensitive to a small
number of outlying values — if one row in the CSV were corrupted into a huge
or tiny number, a plain mean would move a lot but a trimmed mean would barely
move, because the offending row gets dropped before the sum.

## What I changed

`eval.py` now sorts the parsed values, drops the single smallest and single
largest value (`sorted(values)[1:-1]`), and reports the mean of what's left as
`score`. The un-trimmed arithmetic mean is still computed and surfaced under
`metrics.baseline_mean` for local comparison (this key isn't in the
researcher-whitelisted metric list, so it won't appear on the held-out PR
comment, but it's useful when running `arch eval` locally against the public
data). For `n < 3` there's nothing left to trim after dropping both ends, so
the code falls back to the untrimmed mean over all values.

## What I saw

The public sample (`data/public/sample.csv`) is `1, 2, 3, 4, 5` — five
symmetric, evenly-spaced values. Dropping the min (1) and max (5) leaves
`2, 3, 4`, whose mean is 3.0 — identical to the untrimmed arithmetic mean
(3.0, per the baseline in PR #16 and `problem.md`'s stated public mean). This
is expected: trimming a symmetric distribution with no real outliers removes
the same amount of mass from each side, so it doesn't shift the mean. The
public data is not a good test case for showing where trimming and the plain
mean diverge — it would take an asymmetric sample or an actual outlier for the
two methods to disagree. I don't know the shape of the held-out sample, so I
can't predict whether its score differs from 20.0 (the value `problem.md`
states for the plain-mean held-out score); if it does differ, that's evidence
the held-out sample has some asymmetry or outlier that the public sample
lacks, since a symmetric held-out sample would score the same as the plain
mean, exactly as it did here.

## Caveat / what I'd try next

This is a legitimate case where "the score didn't move" is itself the
finding, not a null result to iterate away from — the public data is
symmetric so trimming has no effect on it, and that's a property of the data
rather than a bug in the method. If I were continuing this direction, the
next step would be to add an intentionally asymmetric fixture (e.g. one
outlier value) to `data/public` to actually exercise the divergence between
trimmed and untrimmed means locally, rather than only being able to observe
divergence (or its absence) once the held-out score lands.
