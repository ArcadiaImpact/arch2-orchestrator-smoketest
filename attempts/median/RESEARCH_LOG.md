# Median instead of mean (toysmoke3)

## Direction

`problem.md` seeds direction 3: report the median instead of the mean, and
characterize where the two diverge. As with the other attempts on this run,
the researcher's stated purpose for `arch/toysmoke3` is to exercise the
orchestrator pod's lifecycle (fleet supervision, the fixed wrap-up trigger,
transcript-hashing, the leaderboard tie-break) on a task whose numeric answer
is already known from the two prior passes — so this attempt tests whether a
computation that is *not* `sum(values) / len(values)` still scores correctly
through the held-out pipeline, which is a different pipeline-health check
than the parsing-hardening (#13) and compensated-summation (#14) attempts
already submitted on this run.

## What changed

`eval.py` now computes both `mean = sum(values) / len(values)` (the
direction-1 baseline) and `median = statistics.median(values)`, and reports
`median` as `score` while keeping `mean`, `median`, and their difference
(`mean_minus_median`) in `metrics` for local inspection — `problem.md`
whitelists only `score` off the held-out run, so the extra keys are
public-iteration-only diagnostics, not something a reviewer can see on the
held-out PR comment.

The median and mean characterize a distribution differently: the mean is
sensitive to every value (an outlier at either extreme shifts it), while the
median only depends on the value(s) at the center of the sorted list, so
outliers on one side don't move it. They diverge whenever a distribution is
skewed (mass concentrated more on one side of center) or has an outlier —
they coincide when the distribution is symmetric around its center.

## Local result

```
score: 3.0
```

On the public `sample.csv` (values `1, 2, 3, 4, 5`), `mean` and `median` are
both `3.0` (`mean_minus_median: 0.0`) because the five values are evenly
spaced and symmetric around their middle element. This is the same score
`problem.md` states as the public reference (3.0), so the median-based score
is indistinguishable from the mean-based baseline on this particular fixture
— which is expected, not a sign the two statistics are interchangeable in
general. `problem.md` also states the held-out mean is 20.0; if the held-out
CSV is similarly symmetric (e.g. also evenly spaced), this attempt should
score 20.0 on held-out too, but if the held-out values are skewed or contain
an outlier, this attempt's held-out score would legitimately differ from the
other attempts' — that divergence, if it appears, is the whole point of
submitting this alongside the mean-based attempts.

## What I'd try next

Nothing further needed on the public fixture, since it can't distinguish
mean from median by construction (symmetric, no outliers). Once this PR's
held-out score lands, comparing it against #13/#14's held-out scores (which
both keep the mean) is the actual test of whether the two statistics
diverge on the held-out data — that comparison can't be done locally,
by design, since the held-out CSV is never visible to workers.
