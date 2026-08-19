# Research log — robust CSV parsing for the arithmetic mean baseline

## Context

`problem.md` seeds two directions: (1) compute the arithmetic mean directly,
and (2) try a trimmed/robust mean and compare. My own prior attempts on this
task covered both, plus a third structurally-distinct statistic:

- PR #2 — plain arithmetic mean (direction 1, unmodified baseline).
- PR #3 — trimmed mean (direction 2): average of the middle 60% of sorted
  values after dropping the top/bottom 20%.
- PR #4 — median: the middle order statistic, chosen with no averaging at
  all.

All three scored `20.0` against held-out data (matching the trivial
baseline's stated held-out score), and each research log independently
concluded the same thing: `problem.md` states the held-out task has exactly
one correct value (the true arithmetic mean), so no alternative statistic
can score higher — a statistic other than the plain mean is either a tie
(when the held-out data happens to be symmetric) or strictly worse. PR #4's
log explicitly named the next useful direction as *not* another
alternative-statistic variant, since that's now a confirmed dead end, but
checking robustness of the baseline computation itself.

## Hypothesis

This attempt asks a parsing question, not a statistics question: is the
current baseline's CSV reading robust to a malformed row? The baseline
(`eval.py` on `arch/toysmoke`, and all three prior attempts) parses every
row unconditionally with `float(row["value"])` and no guard. If any row in
the CSV is blank or contains a non-numeric value, this raises an uncaught
`ValueError` and the eval process crashes before writing `$ARCH_EVAL_OUTPUT`.

`problem.md`'s "Two specific misreadings to guard against" section is
explicit that a crashed/never-posting pod produces a `null` score that is
indistinguishable, from the PR alone, from "still running" — the exact
failure mode a parsing crash would cause. `data/public/sample.csv` and
(per `problem.md`) the held-out CSV are both clean, so this failure mode has
never actually been exercised by any prior attempt — it's an untested edge
of the pipeline, not a statistic choice.

## What I did

Changed `eval.py` (the file itself is the trusted scoring path per
`.arch/config.toml`'s `trusted_paths` — only `.arch/` is restored from base,
so `eval.py` is scored as submitted) to:

- Keep the statistic unchanged: still the plain arithmetic mean over all
  valid values (direction 1, untouched).
- Strip and check each row's `value` cell before conversion. A blank cell is
  skipped. A cell that fails `float()` is caught and skipped rather than
  raising.
- Report `skipped` (count of rows dropped) alongside `n` (count of values
  actually averaged) in `metrics`, for local/CI-log visibility. Per
  `.arch/config.toml`'s empty `public_metrics` allow-list, only `score` is
  published on the held-out PR comment, consistent with prior attempts.

## Local result

On the clean `data/public/sample.csv` (1, 2, 3, 4, 5): no rows are skipped,
`arch eval` → `score: 3.0`, identical to the unmodified baseline (PR #2).
This is expected — the public sample has no malformed rows, so this change
is a no-op on the public/held-out score path, exactly like the prior
attempts' ties on the public sample.

To exercise the actual change, I ran `eval.py` directly (not through `arch
eval`, and not committed to the repo) against a throwaway CSV at
`/tmp/testdata/sample.csv` containing the values `1, 2, [blank line],
not_a_number, 3, 4, 5`. Result: `{"score": 3.0, "metrics": {"n": 5, "skipped":
1}, ...}` — the five valid values averaged correctly to 3.0, one malformed
row was dropped and counted, and the process did not crash. (The blank line
produced no row at all from `csv.DictReader` and so isn't counted in
`skipped`; only the non-numeric cell is.) I did not commit this throwaway
file or point `data/public` at it, since it isn't part of the iteration
target — it's a manual exercise of a code path the public/held-out data
doesn't otherwise reach.

## Prediction and what would make this a dead end

Since the statistic is unchanged, I expect this to score identically to PR
#2 on held-out data (20.0), because `problem.md` states the held-out CSV
is clean and well-formed — this change is a no-op there too. If it lands on
anything other than 20.0, that's a hard signal the held-out CSV in this run
actually does contain a malformed row (or that I introduced a parsing bug),
either of which is worth flagging back to the researcher rather than
iterating further on this branch.

## What I'd try next

If robustness turns out to matter (unexpected held-out score), the next
step would be distinguishing "row genuinely missing" (drop and note it, as
here) from "row present but wrong type" (which might warrant a `null` score
instead of silently continuing, since silently averaging over unexpectedly
few values could mask a bigger problem than a single stray row). Since this
task's own framing says the score itself is not a research signal, I don't
plan to chase further parsing edge cases (e.g. non-UTF8 encoding, extra
columns) without a concrete reason to think the held-out data could contain
them.
