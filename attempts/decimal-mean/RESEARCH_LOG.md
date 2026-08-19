# Research log — decimal-mean

## Starting point

Per `findings/toysmoke/problem.md`, this task's actual purpose is to smoke-test
the ARCH 2.0 orchestrator pipeline, not to do real research — the mean of a
tiny CSV has one correct answer, so no statistic can "win." Prior attempts
already covered the seeded directions (arithmetic mean, trimmed mean) plus
median, tolerant CSV parsing, and — most relevant here — PR #6's fix for
floating-point summation error using `math.fsum`.

PR #6's own "Notes / caveats" section flagged that it didn't plan to chase
further precision edge cases without a concrete reason. I found one: `fsum`
fixes summation order, but it doesn't touch the step *before* summation,
where each CSV string is first converted to a binary `float`.

## Idea

Most decimal fractions (0.1, 0.2, 0.3, ...) aren't exactly representable in
binary floating point. `float("0.1")` is already a rounded approximation
before any arithmetic happens. `math.fsum` computes a correctly-rounded sum
*of those approximations* — it can't recover precision that was thrown away
at parse time, and the final division by `len(values)` is itself a rounding
step. So even after PR #6's fix, there are still `n + 1` rounding events
(one per value, one for the division).

Python's `decimal.Decimal` can be constructed directly from a string and
represents the exact decimal digits written in the CSV, with no binary
approximation. Summing and dividing `Decimal` values keeps that exactness
through the whole computation (with Decimal's default 28-digit context
precision, far more than a double's ~15-17 significant digits), so the only
rounding event in the entire pipeline is the final `float(mean)` conversion
needed to serialize a JSON number.

## Verification before changing code

I didn't want to ship this on the strength of "Decimal is more precise" as
an assertion, so I first searched for a concrete example where the two
methods actually disagree. A brute-force search over random 2-decimal-digit
values (see the search script logic, run interactively) turned up cases
like:

```
values = ['0.76','0.42','0.26','0.51','0.4','0.78','0.3']
math.fsum([float(v) for v in values]) / 7   -> 0.49000000000000005
float(sum(Decimal(v) for v in values) / 7)  -> 0.49
```

This confirms the mechanism is real, not hypothetical: `fsum` alone does not
make the pipeline exact, because the lossy step happens earlier, at
`float(row)`.

## What I changed

`eval.py`: read each CSV value as a string and construct `Decimal(v)`
directly (no `float()` in between), sum and divide as `Decimal`s, and only
convert to `float` once, at the very end, for JSON output. Kept the
statistic itself (arithmetic mean) and the CSV row-admission logic
unchanged, so this branches from `arch/toysmoke` directly rather than
stacking on PR #6 or PR #5 — the variable under test here is "how are values
represented," independent of "which statistic" or "which rows are valid."

## Result on public data

`data/public/sample.csv` is `1,2,3,4,5` — integers, which have exact
representations in both binary float and decimal. `arch eval` gives `3.0`,
identical to the baseline, exactly as expected: the public data can't
exercise this failure mode by construction (this is the same limitation PR
#6 noted about itself).

## What I'd try next

If this doesn't move the held-out score either, that's consistent with the
held-out CSV also containing values that happen to be exact in binary (e.g.
integers or fractions with only powers of 2 in the denominator) — plausible
for a small smoke-test file. Per problem.md's framing, I don't think there's
a principled reason to keep stacking numerical-precision fixes without
evidence the held-out data actually contains values that expose them; if a
future attempt wants to keep digging in this direction, the next
distinguishable question would be exact rational arithmetic (`fractions.Fraction`)
to see whether it fixes any case Decimal doesn't. But absent that evidence, I'm
not treating this attempt itself as motivation for a fourth precision-focused
PR — its purpose is to close out one clean question (does removing the
initial float-conversion rounding matter beyond fixing summation order), not
to open a new one.
