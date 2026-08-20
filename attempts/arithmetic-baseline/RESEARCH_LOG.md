# Arithmetic mean baseline (toysmoke3)

## Direction

`problem.md` seeds direction 1: verify the direct `sum(values) / len(values)`
computation end to end, and confirm it is the reference every other
direction on this run is compared against. This run repeats the same toy
task as `arch/toysmoke` and `arch/toysmoke2` to exercise the orchestrator
pod's lifecycle (fleet supervision, fixed wrap-up trigger, transcript-
hashing, leaderboard tie-break); per `problem.md`, every correct attempt
lands on the same score, so this attempt's purpose is not to improve on the
number but to give this run's own leaderboard an unmodified reference point,
submitted as its own labeled PR rather than only existing implicitly as the
untouched `eval.py` on the base branch.

## What changed

Nothing in `eval.py`. This attempt commits the file unchanged from the
`arch/toysmoke3` base branch: it reads `sample.csv` with `csv.DictReader`,
converts every `value` cell with `float()`, and computes
`sum(values) / len(values)` directly, with no parsing hardening, no
alternate summation strategy, and no alternate statistic. That is
deliberate — this attempt exists to be the thing the other three attempts on
this run (#13 robust parsing, #14 compensated summation, #15 median) are
each a one-axis variation of, so that once held-out scores land, each of
their deltas can be read against this PR specifically instead of against an
unlabeled base branch.

## Local result

```
score: 3.0
```

Matches the public reference mean stated in `problem.md` exactly, as
expected for an unmodified baseline. If the held-out score for this PR comes
back as anything other than 20.0 (the held-out reference mean stated in
`problem.md`), that would indicate a problem with the eval pipeline itself
(volume mount, scorer restoration, or the publish path) rather than with any
of this run's method variants, since this attempt makes no computational
change to falsify.

## What I'd try next

Nothing — this attempt is intentionally a no-op relative to the base branch,
and its only role is as the fixed reference point for the other three
attempts submitted on this run. Any further work belongs in a
differentiated attempt (parsing, summation, or statistic), not here.
