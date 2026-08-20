# Compensated summation (toysmoke3)

## Direction

`problem.md` seeds direction 5: use `math.fsum` (or Kahan summation) so
floating-point error does not accumulate across the sum, instead of the
builtin `sum()`. As with the other seeded directions in this run, the
researcher's stated purpose for `arch/toysmoke3` is to exercise the
orchestrator pod's lifecycle (fleet supervision, the fixed wrap-up trigger,
transcript-hashing, the leaderboard tie-break) rather than to find a
numerically different answer — the task's own problem statement says every
correct attempt lands on the same score, so this attempt is submitted as a
distinct pipeline-health data point (does the eval still produce the right
number when the summation strategy changes, and does the CI/scoring chain
handle a metrics dict with more numeric keys), not as an attempt to move the
score.

## What changed

Python's builtin `sum()` adds floats left to right with ordinary
double-precision rounding at each step; for long sequences of
similar-magnitude floats this rounding error can accumulate to a visible
amount. `math.fsum` tracks partial sums with full precision (Shewchuk's
algorithm) and only rounds once at the end, so it is immune to that
accumulation. I changed `eval.py` to compute the mean from
`math.fsum(values)` instead of `sum(values)`, and additionally report both
the naive and compensated sums plus their delta (`sum_delta`) in `metrics`
so a reviewer can see directly whether the two methods diverged on this
input — `problem.md` says only `score` is whitelisted out of held-out runs,
so these extra keys are for local/public inspection only and won't appear on
the held-out PR comment.

## Local result

```
score: 3.0
```

`sum_delta` was `0.0` on the public `sample.csv` (values `1, 2, 3, 4, 5`) —
unsurprising, since small integers summed in a 3-5 element list have no
floating-point rounding to correct in the first place. This is the expected
outcome for this dataset: `math.fsum` and `sum()` only diverge once you're
summing many terms or terms of very different magnitudes, neither of which
this toy CSV has. The change is a no-op here by construction, which is
consistent with what the problem statement says about this run — there is no
method-comparison signal to be found, only a confirmation that switching the
summation implementation doesn't break the eval or its output contract.

## What I'd try next

Nothing further on this axis for this dataset — there's no floating-point
error to observe here, so there's nothing left to characterize. If a future
pass wanted to actually exercise the naive/compensated divergence, it would
need a held-out (or public) fixture built to have many terms or extreme
magnitude spread, but fabricating that fixture would be changing the task's
data to manufacture a result, which is out of scope for a smoke test whose
data is fixed by the researcher.
