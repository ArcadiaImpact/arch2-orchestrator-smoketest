# Attempt: arithmetic mean (direction 1)

## What I checked

`problem.md` and the task's `eval.py` define the target as "the mean of
values in sample.csv." `eval.py` already implements this directly: it reads
the `value` column and computes `sum(values) / len(values)` — the standard
arithmetic mean, no filtering or weighting. Against `data/public/sample.csv`
(values 1..5) this gives 3.0, matching the trivial-baseline number quoted in
`problem.md`.

Since the computation is already correct, there was no code to fix. What I
added is `verify_mean.py`, a small independent script that re-reads
`sample.csv` from `ARCH_DATA_ROOT` and recomputes the mean the same way, so
the "direction 1" hypothesis (compute the arithmetic mean directly) is a
standalone, checked-in artifact that can be re-run and cross-checked against
whatever `eval.py` reports, rather than just an assertion in this log. Running
it against the public sample reproduces 3.0, matching `eval.py`.

## Why I expect this to hold on held-out data

`problem.md`'s "Why this measurement makes sense" section is explicit that
this task has exactly one correct value (the arithmetic mean of the held-out
CSV) and that a non-null 20.0 on this PR is evidence the held-out pipeline
(label → workflow trigger → pod scheduling → volume mount → eval → sanitized
publish) ran end to end — it is not evidence of a better "method," since
there is no method space here beyond getting the arithmetic mean right. This
attempt is deliberately the control point: if this PR doesn't land on 20.0,
the problem is in the orchestration/eval pipeline, not in any statistic I
chose.

## What I'd try next

The seeded direction 2 (trimmed/robust mean) is a genuinely different
computation and is worth submitting separately to see whether it diverges
from this baseline on held-out data — see the sibling attempt
`attempts/trimmed-mean` if present on the leaderboard.
