# Research log — precise-sum

## Starting point

Four attempts already sit on the leaderboard, all scoring 20.0 on held-out
data: PR #2 (plain arithmetic mean, the control), PR #3 (trimmed mean), PR
#4 (median), and PR #5 (tolerant CSV parsing for blank/non-numeric rows).
PR #2's research log frames itself as the pipeline's control point, and PR
#3/#4 both concluded that no alternative statistic beats the plain
arithmetic mean, because `problem.md` defines the target as exactly the
arithmetic mean of the held-out CSV — there is only one correct number, so
"which statistic" is a closed question. PR #5 closed the "is the parser
robust to bad rows" question instead.

That left an angle none of the four had touched: not *which* value to
compute, and not *which rows* to admit, but *how the arithmetic itself is
carried out* once the values are already known-good floats.

## Hypothesis

`.arch/eval.sh`'s own header (shared by every attempt, not something I
added) carries this warning verbatim: "Python addition gives
`5.000000000000004` from arithmetically-clean inputs and silently fails the
gate. Always: `round(value, 2)` before the gate, and round again before
serializing to JSON." It's written for threshold gates, but the underlying
mechanism — plain `sum()` accumulates float rounding error left-to-right —
applies just as much to `eval.py`'s own `sum(values) / len(values)`. If the
held-out `sample.csv` contains values that don't sum cleanly in binary
floating point (anything with repeating binary fractions, e.g. tenths), the
naive sum could be off in the last bit or two from the true mean, and that
noise could also leak into the serialized JSON as a long trailing-digit
float instead of a clean number.

`data/public/sample.csv` is `1, 2, 3, 4, 5` — small integers that happen to
sum exactly in floating point, so this failure mode is invisible on the
public data. That is itself worth flagging: a bug class can be fully masked
by an unlucky-clean public sample, which is exactly the kind of thing
`problem.md` says the held-out split exists to catch.

## What I did

Rather than trust the mechanism by description, I reproduced it directly
before touching `eval.py`:

```python
vals = [0.1]*10 + [0.3]
naive = sum(vals) / len(vals)      # 0.11818181818181817
precise = math.fsum(vals) / len(vals)  # 0.11818181818181818
naive == precise                    # False
```

Eleven ordinary-looking decimal values are enough to make plain `sum()`
and `math.fsum()` (Python's compensated/Neumaier summation, immune to
intermediate rounding error regardless of order) disagree in the last
digit. That confirms the mechanism is real, not hypothetical, before
spending a PR on it.

I then changed `eval.py`'s computation from `sum(values) / len(values)` to
`round(math.fsum(values) / len(values), 10)` — same statistic (the
arithmetic mean, direction 1, unchanged), same row-admission logic as the
pre-PR#5 baseline (this attempt branches from `arch/toysmoke` directly, not
from PR #5, to keep the two robustness concerns — bad rows vs. summation
precision — isolated and independently reviewable). The 10-decimal rounding
follows the eval.sh guidance to round before serializing, at a precision
loose enough to never change a value that matters but tight enough to strip
float-repr noise from the JSON output.

`arch eval` on public data still prints `3.0`, unchanged — expected, since
`1+2+3+4+5` sums exactly regardless of method.

## What I'd conclude, and what I'd try next

I expect this to score 20.0 on held-out, identically to PR #2, for the same
reason PR #5 expected an identical score: if the held-out CSV's values also
happen to sum cleanly (plausible, since problem.md implies it's a similarly
small, simple file), this change is a no-op there too, and the only
evidence it did anything is the absence of float noise in a value nobody
downstream inspects at that resolution. If it does *not* land on 20.0, that
would be surprising and worth flagging rather than iterating further —
either the held-out file is large/adversarial enough for summation order to
matter (unlikely for a smoke test) or I introduced a rounding bug.

Given `problem.md`'s explicit framing that this task has no real hypothesis
space left to explore once the statistic and the parser are both settled, I
don't plan to chase further numerical-precision edge cases (e.g. `Decimal`
for exact base-10 arithmetic, Kahan summation implemented by hand instead of
relying on `math.fsum`) without a concrete reason to think the held-out data
is large or adversarial enough to need them. The more useful next step, if
this run continues, is probably back to the actual thing under test per
problem.md: watching orchestrator behavior (stall detection, deadline
wrap-up), not further variations on a 3-row mean.
