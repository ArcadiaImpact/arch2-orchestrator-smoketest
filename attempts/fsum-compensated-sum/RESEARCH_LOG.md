# Compensated summation (`math.fsum`) — research log

**Direction:** #5 from the seeded hypothesis space in `findings/toysmoke4/problem.md`
— use `math.fsum` instead of the builtin `sum()` so floating-point rounding
error doesn't accumulate across the summation step of the mean.

## Idea

`eval.py`'s baseline computes the mean as `sum(values) / len(values)`.
Python's builtin `sum()` adds floats left to right, and each addition can
introduce a small rounding error because most decimal fractions (e.g. `0.1`)
have no exact binary floating-point representation. Over many additions these
errors can accumulate. `math.fsum()` implements the Shewchuk algorithm, which
tracks the rounding error at each step and folds it back in, producing a
correctly-rounded result for the true mathematical sum of the inputs.

## What I did

Changed one line in `eval.py`: `score = sum(values) / len(values)` became
`score = math.fsum(values) / len(values)`. I kept both sums (`plain_sum` via
`sum()`, `compensated_sum` via `math.fsum()`) plus their difference in the
`metrics` object (not on the public allow-list per `.arch/config.toml`, so
visible only to someone reading the raw eval output) so the two paths can be
compared directly instead of the change being an unverified assertion.

## What I found

On this task's actual data, the two methods agree exactly. The public
sample is `[1, 2, 3, 4, 5]` and the held-out sample is `(10, 20, 30)` per
`problem.md` — both are small sets of integers that are exactly representable
in binary floating point, so there is no rounding error for `fsum` to correct
in the first place. `arch eval` on the public data returns `score: 3.0`,
identical to the arithmetic-mean baseline in #22, and `sum_diff` in the
metrics is `0.0`.

Because `arch eval` can't show a difference on real data, I added
`attempts/fsum-compensated-sum/demo_fsum_gap.py`, a standalone script (not
part of the scored path) that sums ten copies of `0.1` — a value with no
exact binary representation — and shows `sum()` returning `0.9999999999999999`
while `math.fsum()` returns exactly `1.0`. That's the mechanism this change
guards against; it just isn't exercised by this task's fixed inputs.

## What I'd try next

To actually observe divergence on the scored path, the input data would need
either (a) many more rows, since rounding error grows with the number of
additions, or (b) values with non-terminating binary representations (like
`0.1`, `0.2`, `0.3`) rather than small integers. Neither is available in this
task's fixed public/held-out files, so this attempt is a "confirmed no-op on
this data, mechanism demonstrated separately" result rather than a numeric
improvement — consistent with `problem.md`'s statement that all six seeded
directions are expected to return the same score here.
