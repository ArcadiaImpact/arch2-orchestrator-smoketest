# Research log — median vs. arithmetic mean

## Context

`problem.md` seeds two directions: (1) compute the arithmetic mean directly,
and (2) try a trimmed/robust mean and compare. My own prior attempt (PR #3,
branch `arch-toysmoke-attempt-trimmed-mean`) covered direction 2 by changing
`eval.py` to drop the top/bottom 20% of sorted values and average the rest.
This attempt tests a third option, not explicitly seeded but a natural
extension of the same question: the median.

## Why the median is a genuinely different test, not a variant of direction 2

A trimmed mean and the median are both "robust" statistics in the informal
sense that they're less sensitive to extreme values than the plain average.
But they get there by different mechanisms:

- A trimmed mean still *averages* a subset of the data — it's an arithmetic
  mean computed over fewer points.
- The median (for odd `n`, which is what both the public sample and, per
  `problem.md`, the held-out sample have — 3 rows) is a single order
  statistic. It does not sum or average anything; it picks one value and
  discards the magnitude information of every other value.

So this attempt asks a structurally different question from PR #3: not "does
discarding tails change the answer" but "does using *no* averaging at all,
just positional information, change the answer." Since `problem.md` states
the task has exactly one correct value (the true arithmetic mean of the
held-out CSV), I expect this to score at or below 20.0, same prediction as
PR #3 — but for a different reason worth having as a separate data point:
if the held-out data is symmetric around its mean, an odd-`n` median can
coincide with the mean exactly (as happens on the public sample below);
if it isn't, the median diverges from the mean in a way that has nothing to
do with tail-trimming.

## What I did

Changed `eval.py`'s scoring computation (the file itself, since only `.arch/`
is a trusted path per `.arch/config.toml` — `eval.py` is what the held-out
pod actually scores) to compute the median of the `value` column instead of
`sum(values) / len(values)`. The untouched arithmetic mean is still computed
and stored under `metrics.arithmetic_mean` for local/CI-log comparison, but
per `.arch/config.toml`'s empty `public_metrics` allow-list it is not
surfaced on the PR comment — only `score` is.

## Local result

On `data/public/sample.csv` (values 1, 2, 3, 4, 5 — symmetric, n=5, odd):
median = 3, which ties the arithmetic mean (also 3.0) exactly, and also ties
PR #3's trimmed mean. `arch eval` → `score: 3.0`.

This tie is uninformative about held-out behavior for the same reason noted
in PR #3: the public sample happens to be symmetric, so any reasonable
central-tendency statistic collapses to the same number here. Only the
asynchronous held-out score can distinguish this hypothesis, since
`problem.md` states the held-out CSV has a different number of rows (3) than
the public sample (5) and no claim is made about its symmetry.

## Prediction and what would make this a dead end

I expect this to score at or below 20.0, never above — `problem.md` is
explicit that the task has no "more correct than correct" answer beyond the
true arithmetic mean of the held-out data. If the held-out score comes back
below 20.0, I'll treat "order-statistic estimators" (median, and by
extension any quantile-based approach) as a confirmed dead end alongside
trimmed means, and won't submit further variants (e.g. weighted median,
different tie-breaking for even n) chasing a closer number — that would be
fitting to the metric rather than testing the hypothesis.

## What I'd try next

Given the task's own framing (`problem.md`: "the score is not a research
signal at all... every correct attempt lands on 20.0 and every incorrect one
does not"), I don't think further central-tendency variants (geometric mean,
harmonic mean, mode) add new information beyond what PR #3 and this attempt
already establish: any statistic other than the plain arithmetic mean is
expected to underperform on a task whose target is definitionally the
arithmetic mean. The more valuable next step, if continuing, would be
verifying edge-case robustness of the baseline computation itself (e.g.
empty/missing values, non-numeric rows) rather than proposing more
alternative statistics.
