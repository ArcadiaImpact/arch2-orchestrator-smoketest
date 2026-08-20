# Robust CSV parsing — research log

## Direction

Direction 4 from the seeded hypothesis list (`findings/toysmoke3/problem.md`):
harden the CSV reader so a malformed, blank, or non-numeric row cannot crash
`eval.py`, while leaving the arithmetic-mean computation itself unchanged.

## Why this direction

The original `eval.py` builds `values` with a single list comprehension,
`[float(row["value"]) for row in csv.DictReader(f)]`. Any row where the
`value` column is empty or non-numeric raises an uncaught `ValueError` and
the eval process crashes with a traceback instead of writing a score. On the
held-out side, that failure mode is indistinguishable from a dead
orchestrator pod — both show up as a PR with no score comment
("Two score misreadings to guard against", `problem.md`). Since this run's
whole point is exercising the orchestrator's wrap-up and scoring pipeline,
removing a plausible cause of a silent null score is directly useful, even
though the held-out CSV is expected to be clean.

## What I changed

In `eval.py`, replaced the list comprehension with an explicit loop over
`csv.DictReader(f)` that:

- strips the `value` field and skips the row (counting it as `skipped`) if
  it is empty after stripping,
- attempts `float(raw)` and skips the row (again counting it) on
  `ValueError` instead of propagating the exception,
- raises only if **no** row parses at all (an all-bad file is a real error,
  not something to silently score as 0).

The final `score = sum(values) / len(values)` line is untouched — this is
still the direct arithmetic mean from direction 1, computed over whatever
rows survived parsing. `skipped` is surfaced in `metrics` and `notes` for
local debugging, but per `problem.md` only `score` is whitelisted for
publication on held-out PRs, so this doesn't leak anything about the
held-out file's shape.

## Result

- `arch eval` against `data/public/sample.csv` (5 clean rows, values
  1..5): **score 3.0**, `skipped: 0` — identical to the arithmetic baseline,
  confirming the hardening is a no-op on well-formed input.
- Manual test against a synthetic dirty CSV (`1, "", 2, abc, 3, 4, 5`,
  i.e. a blank row and a non-numeric row injected among the same 1..5
  values): still computed **3.0**, with `skipped: 1` reported (the CSV
  module itself drops the fully-blank line before `DictReader` sees it, so
  only the non-numeric row hits the explicit skip path). This confirms the
  crash path is actually closed, not just theoretically closed.

## What I'd try next

If this were a real research task rather than an orchestrator smoke test,
the next step would be deciding what a *majority*-bad file should do —
right now `skipped` has no threshold, so a file that is 99% garbage still
silently returns a mean over the 1% that parsed. A stricter version could
fail loudly above some skip-ratio rather than only failing on 100% bad
rows. Out of scope here since the held-out file is known-clean and the
point of this pass is orchestration, not the statistic.
