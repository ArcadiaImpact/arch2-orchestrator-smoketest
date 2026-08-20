# Median attempt — research log

## Direction

Direction 3 from the seeded hypothesis space: use the median instead of the
mean, and characterise where the two diverge. Builds on PR #22 (arithmetic
mean baseline, direction 1), which verified the baseline mean computation
independently and established it as the reference point.

## What I did

Changed `eval.py`'s scored value from `sum(values) / len(values)` (mean) to
`statistics.median(values)`, and kept both the mean and the median in the
`metrics` object for comparison (`metrics` keys are not on the public
allow-list per `.arch/config.toml`, so they're for internal/reviewer use
only, not surfaced on the PR comment).

## Result: median equals mean here, and that itself is the finding

Running `arch eval` against `data/public/sample.csv` ([1, 2, 3, 4, 5]) gives
`score: 3.0` — identical to the mean baseline in PR #22. This is not a bug in
either attempt; it's a property of the data. For an odd-length, symmetric
list (values evenly spaced around a center, here 1..5 centered on 3), the
middle element *is* the arithmetic mean, so mean and median are
mathematically forced to coincide. `findings/toysmoke4/problem.md` states the
held-out sample is `(10, 20, 30)`, which is also odd-length and symmetric, so
I expect the held-out score for this attempt to also come back as 20.0 —
same as PR #22 — for the identical reason, not because the eval path is
broken.

So this attempt does *not* "characterise where the two diverge" in the sense
of finding a numeric gap — with this particular public/held-out data there
is no gap to find. The useful result is narrower but still real: it pins
down *when* mean and median are guaranteed to agree (odd n, symmetric
distribution) versus when they would not (even n, or any skew/outliers in
the values). Neither the public nor the held-out sample as described in
`problem.md` falls into the second case, so this task's fixed data cannot
distinguish the two estimators — a limitation of the toy data, not of the
method.

## What I'd try next

To actually observe mean/median divergence, the input list itself would need
to change (e.g. add an outlier or make the count even) — but the public and
held-out CSVs are fixed inputs to this task, not something a worker attempt
should alter, since doing so would change what's being measured rather than
how it's measured. A more informative next step within the current
constraints is direction 4 (robust CSV parsing), which is testable without
needing different input values — a malformed/blank row is a code-path
difference, not a data-value difference.
