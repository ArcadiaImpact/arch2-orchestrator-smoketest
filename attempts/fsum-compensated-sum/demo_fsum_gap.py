"""Standalone demo of where plain sum() and math.fsum() diverge.

Not part of the scored eval path -- this exists only to show the mechanism
that motivates the change in eval.py, since neither the public sample
([1,2,3,4,5]) nor the held-out sample (10, 20, 30, per problem.md) contains
values whose binary floating-point representation is inexact, so `arch eval`
on this task's real data cannot show a difference between the two sums.

`sum()` adds floats left-to-right and accumulates one rounding error per
addition. `math.fsum()` uses the Shewchuk algorithm to track the rounding
error exactly and correct for it, giving a correctly-rounded result for the
true mathematical sum of the inputs.
"""
import math

values = [0.1] * 10  # each 0.1 is not exactly representable in binary float

plain = sum(values)
compensated = math.fsum(values)

print(f"sum(values)       = {plain!r}")
print(f"math.fsum(values) = {compensated!r}")
print(f"difference        = {compensated - plain!r}")
assert plain != 1.0, "expected plain sum to show rounding error on this input"
assert compensated == 1.0, "expected fsum to recover the exact result"
print("OK: fsum corrects the accumulated rounding error that sum() leaves in.")
