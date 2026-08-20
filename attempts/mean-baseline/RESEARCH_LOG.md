# Mean baseline verification — research log

## Direction

Direction 1 from the seeded hypothesis space: verify that `eval.py`'s
arithmetic-mean computation (`sum(values) / len(values)`) is correct end to
end, and confirm it is the reference every other direction (trimmed mean,
median, compensated summation, `Decimal` arithmetic, etc.) should be compared
against. See `findings/toysmoke4/problem.md` for the full task framing.

## What I did

`eval.py` already reads `data/public/sample.csv` with `csv.DictReader` and
computes `sum(values) / len(values)`. No change to `eval.py` was needed — this
attempt's job was to confirm that computation is actually right, rather than
assume it because the code reads simply.

I wrote `attempts/mean-baseline/verify_baseline.py`, a second, independent
implementation of the same formula that:

1. Parses `data/public/sample.csv` on its own (separate code path from
   `eval.py`, so a bug shared by both would still be caught by comparing
   against a hand-computed expected value, not just by the two paths
   agreeing with each other).
2. Asserts the parsed values are exactly `[1.0, 2.0, 3.0, 4.0, 5.0]` — i.e.
   that the CSV is what `problem.md` says it is, not just "some numbers."
3. Asserts the computed mean equals `3.0`, the value hand-derived from
   `(1+2+3+4+5)/5`.

Running it (`python3 attempts/mean-baseline/verify_baseline.py`) prints `OK`
and the matching value. Running `arch eval` separately also returns
`score: 3.0` on the public data, matching the problem statement's claim that
public data means 3.0.

## Why this should move nothing on its own, and that's the point

Per `problem.md`, every correct implementation of "mean of a column" scores
20.0 on the held-out data because the held-out sample (10, 20, 30) is
symmetric and exactly representable in binary floating point — there is no
score gradient between the arithmetic mean and any of the other seeded
directions. So this attempt isn't trying to raise the score; it exists to
establish the reference point (arithmetic mean = correct, byte-for-byte
verified against a hand-computed expected value) that later attempts on this
branch (trimmed mean, median, compensated summation, `Decimal`) can cite when
they claim to "match the baseline" or "diverge from it." Without this
verification step, "the baseline is right" would be an unstated assumption
carried over from three prior identical toy runs rather than a checked fact
in this run's own PR history.

## What I'd try next

If I continue past this attempt: direction 3 (median) is the most likely to
produce a numerically distinct result from this baseline (a median differs
from a mean whenever the distribution isn't symmetric), so it's the
cheapest way to produce a genuinely different number to reason about — more
informative than trimmed mean or compensated summation, which are
expected to equal the arithmetic-mean baseline exactly on both the public
and the held-out samples given in `problem.md`.
