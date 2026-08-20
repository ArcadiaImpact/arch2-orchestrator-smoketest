# Research log — arithmetic mean baseline

## Idea

Research direction 1 in `findings/toysmoke2/problem.md` asks for the
arithmetic mean baseline (`sum(values) / len(values)`) to be verified
end to end, since every other seeded direction (trimmed mean, median,
robust parsing, compensated summation, `Decimal` arithmetic) is meant to
be compared against it. The existing `eval.py` already implements this
computation, so the useful contribution here is *verification*, not a
rewrite: confirm the shipped baseline is correct rather than just trust
it.

## What I did

Added `attempts/mean-baseline/verify_mean.py`, a small standalone script
that:

1. Loads `value` from a `sample.csv` (defaults to `data/public/sample.csv`).
2. Computes the mean two independent ways — the same `sum(values) /
   len(values)` eval.py uses, and Python's standard-library
   `statistics.mean`, which uses a different internal algorithm (exact
   fraction accumulation, not raw float division).
3. Asserts the two agree, and prints both results.

I deliberately left `eval.py` untouched. The point of this attempt is to
check the reference computation, not to change it — changing it would
make this attempt indistinguishable from a "new method" PR when it's
meant to be a correctness check on the existing one.

## What I saw

On the public sample (`values = 1, 2, 3, 4, 5`), both computations give
exactly `3.0`, matching the documented public mean in `problem.md`. Ran
`arch eval` locally and got `score: 3.0`, confirming the eval shim,
`ARCH_DATA_ROOT` wiring, and the baseline computation all agree end to
end on the public path.

## What this does and doesn't tell us

Per `problem.md`, the held-out sample (`10, 20, 30`) is symmetric, so
`sum/len` and `statistics.mean` are expected to agree there too — this
check can't surface a divergence on *this* task's data no matter which
method wins. Its value is narrower: it confirms the baseline
computation itself isn't silently wrong (e.g. an off-by-one in `len`,
or a float-accumulation bug) before other attempts cite it as the
reference to compare against.

## Next steps

None planned for this specific check — it's a one-shot verification, not
a method with room to iterate. Other attempts in this run (trimmed mean,
median, `Decimal` arithmetic, compensated summation, robust parsing)
should cite this PR as the baseline they diverge from or agree with.
