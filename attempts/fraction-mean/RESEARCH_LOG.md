# Research log — exact-rational mean via `statistics.mean`

## Idea

The six seeded directions in `findings/toysmoke3/problem.md` include two prior
routes to a more precise mean than plain `sum(values) / len(values)`:
compensated binary-float summation (`math.fsum`, direction #5) and exact
base-10 arithmetic (`decimal.Decimal`, direction #6). This run's leaderboard
already has an attempt for each of the six seeded directions (arithmetic
baseline, trimmed mean, median, robust CSV parsing, `fsum`, and `Decimal`),
and the same six were explored again in each of the two prior runs
(`arch/toysmoke`, `arch/toysmoke2`) — see the "Prior attempts referenced"
section below. Rather than repeat one of those, this attempt tries a third,
previously-unexplored route to precision: Python's standard-library
`statistics.mean`.

`statistics.mean` does not sum the input floats directly. Internally it
converts each value to an exact `fractions.Fraction` (arbitrary-precision
numerator/denominator, so the conversion from a `float` is exact — it
captures precisely the binary value the `float` already holds, with no
additional rounding), sums those Fractions exactly, divides exactly, and
converts back to `float` only once, at the very end. This is mechanistically
different from both prior precision attempts: `fsum` stays in binary
floating-point the whole time and only makes the *order of summation*
numerically stable; `Decimal` re-represents the numbers in base 10 to avoid
binary-fraction representation error. `statistics.mean` avoids intermediate
rounding error entirely by working in exact rationals, regardless of radix.

## What I did

In `eval.py`, computed `naive_mean = sum(values) / len(values)` (the direction
#1 baseline) alongside `fraction_mean = statistics.mean(values)`, and reported
`fraction_mean` as `score`. `naive_mean` and a `means_agree` boolean are kept
in `metrics` purely as a local cross-check — per `problem.md`'s publish
allow-list, only `score` is surfaced from a held-out run, so this doesn't leak
anything about held-out data shape.

## Result

`arch eval` against `data/public/sample.csv` (values `1,2,3,4,5`): `score:
3.0`, identical to the arithmetic baseline, with `means_agree: true`.
Expected: on all-integer input, every one of `sum/len`, `fsum`, `Decimal`, and
`Fraction`-based summation is exact, so there is nothing for any of these
methods to diverge on. This attempt, like the `fsum` and `Decimal` attempts
before it, cannot demonstrate its own value on the shared public fixture —
only on inputs with values that don't have exact short binary representations
(e.g. `0.1`, `0.2`, `0.3`) would `Fraction`-based summation's lack of
intermediate rounding show up as a different (more accurate) result than
plain float summation. I deliberately left the shared `data/public/sample.csv`
fixture unchanged rather than adding such values to it, to keep this attempt
isolated to one hypothesis (per the same reasoning #18's log gives for not
mutating the public fixture in that PR).

## Prior attempts referenced

- Direction #5 (`math.fsum`) and #6 (`decimal.Decimal`) are both already
  represented in this run's leaderboard for `arch/toysmoke3`, and in both
  `arch/toysmoke` and `arch/toysmoke2` before it. This attempt is not a
  duplicate of either: it targets the same general problem (float summation
  error) but through a third, distinct mechanism (exact rational arithmetic
  via `fractions.Fraction`, as used internally by `statistics.mean`) that
  none of the three runs of this task have tried before.

## What I'd try next

Same follow-up as the `fsum` and `Decimal` attempts: a local-only synthetic
CSV with values chosen to have non-terminating binary expansions (e.g.
`0.1, 0.2, 0.3`) would let all three precision routes (`fsum`, `Decimal`,
`Fraction`) be compared directly against plain float summation and against
each other, rather than each being validated only for "doesn't regress the
baseline on clean integer input."
