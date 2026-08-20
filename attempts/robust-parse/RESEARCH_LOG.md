# Robust CSV parsing (toysmoke3)

## Direction

`problem.md` seeds direction 4: harden the CSV reader so a malformed, blank,
or non-numeric row cannot crash the eval. This run (`arch/toysmoke3`) is a
straight re-run of the same toy task explored in `arch/toysmoke` and
`arch/toysmoke2` — the researcher's stated goal for this pass is to exercise
the orchestrator pod's lifecycle (fleet launch/monitor separation, the fixed
wrap-up trigger, transcript-hashing, and the leaderboard tie-break), not to
find a new answer to "what is the mean of this CSV." Since the score itself
carries no research signal here (every correct method lands on the same
number), the only thing worth improving is whether the eval is robust enough
to keep producing that number under input conditions the current baseline
doesn't handle.

## What changed

The baseline `eval.py` reads `sample.csv` with `csv.DictReader` and does
`float(row["value"])` unconditionally. Three ways malformed input can crash
this: a row with an empty `value` cell (`float("")` raises `ValueError`), a
row missing the `value` key entirely (`row["value"]` raises `KeyError` on a
short row), or a row where `value` holds non-numeric text (`float("abc")`
raises `ValueError`).

The change (`eval.py`) pulls parsing into a `load_values()` helper that
iterates rows, treats a missing/blank `value` field as skippable, and wraps
the `float()` conversion in a `try/except ValueError` — a bad row is counted
in a `skipped` counter and excluded from the mean rather than raising. If
every row turns out to be unparseable, the eval reports `score: null` with an
explicit `"no numeric rows found"` note instead of crashing on
`ZeroDivisionError`, which matters for this run's own guidance: a `null`
score is indistinguishable from "still running," so it's better for a truly
empty/corrupt input to produce that same null-with-note outcome than an
uncaught traceback that also just shows up as a missing comment.

On the current public and (presumably) held-out `sample.csv`, every row is
well-formed, so `skipped` is `0` and the score is unchanged — this is a
robustness change, not a computation change, and should not move the score at
all on clean data.

## Prior attempts referenced

This is functionally identical to `arch-toysmoke2-attempt-robust-parsing`
(itself following `arch-toysmoke-attempt-robust-parse`), re-applied to the
`arch/toysmoke3` base branch. It is deliberately not a new algorithmic idea:
the problem statement for this run explicitly says the same six directions
are being re-seeded on purpose so this run's leaderboard is comparable to the
prior two, and that the score's only real signal this time is pipeline
health, not method comparison. Re-running an already-validated hardening
patch checks that the orchestrator pod correctly builds, evals, and scores a
non-trivial diff (not just the untouched baseline) end-to-end on this pass's
infrastructure.

## Local result

```
score: 3.0
```

Matches the public reference mean stated in `problem.md` (3.0), with
`skipped: 0` — confirms the hardened path is a no-op on clean input, as
expected, and did not introduce a regression.

## What I'd try next

Nothing further from this angle — the fix is complete for the stated
failure modes (blank cell, missing key, non-numeric text, all-empty file).
If a future pass wants to extend hardening, the next gap would be duplicate
header rows or a `value` column with a different name/case, but neither is
present in this task's data and inventing them would be fabricating a
problem the task doesn't have.
