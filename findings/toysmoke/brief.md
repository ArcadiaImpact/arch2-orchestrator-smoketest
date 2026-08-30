# Fault-tolerant parsing for a column summary

## Problem

Summarising a CSV column presupposes that the column parses. The
straightforward implementation — convert every `value` cell to a float and
average the results — makes that presupposition silently, and fails hard
when it is violated: a blank cell or a stray non-numeric entry raises during
conversion and terminates the process before any result is produced.

The cost of that failure mode is larger than it looks, because of how the
absence of a result gets interpreted. A run that dies mid-parse and a run
that is still in progress are indistinguishable from the outside — both
simply have no output. So a localised data-quality problem in one row does
not present as a data-quality problem at all; it presents as an
infrastructure problem, and gets investigated as one. The question here is
whether the summary can be made to degrade gracefully instead, reporting a
result over the rows that are valid rather than none at all.

## Method

The statistic is unchanged: the plain arithmetic mean over the `value`
column. Only the parsing step differs.

Rather than converting rows in a comprehension, each row is examined
individually. The `value` cell is fetched defensively and stripped of
surrounding whitespace. An empty cell is counted as skipped and passed over.
A non-empty cell is converted inside a `try`, and a conversion failure is
likewise counted and passed over rather than propagated. The mean is then
taken over the values that did convert.

The count of skipped rows is not discarded — it is reported alongside the
result as `metrics.skipped`, next to `metrics.n`, the number of rows that
contributed. This is the part that makes the tolerance safe rather than
merely convenient: silently averaging over an unknown subset of the data
would trade a loud failure for a quiet one. With both counts reported, a
consumer can see exactly how much of the input was used and decide whether
the result is trustworthy.

## Result

On the development sample, which is clean, the mean is 3.0 with zero rows
skipped — identical to the strict implementation, confirming the change is
inert on well-formed input. On a separate evaluation sample not available
during development, the same computation returns 20.0, again with no rows
skipped, so that sample is well-formed too.

The tolerant path was exercised directly against a deliberately malformed
file containing a blank line and a non-numeric entry. The strict
implementation raises on that input; the tolerant one reports the mean over
the five valid rows and records one skipped, which is the intended
behaviour.

Because neither of the two real samples contains a malformed row, this work
demonstrates that the change is behaviour-preserving on valid data and that
the recovery path works when deliberately provoked. It does not show that
the recovery path has ever been needed on real data, and no claim is made
that it has.

## Limitations

One failure mode survives. If every row is skipped, the mean is taken over
an empty list and the division raises — the same crash-before-output
behaviour the change was meant to eliminate, now triggered by a wholly
malformed file rather than a partly malformed one. Handling that case
requires deciding what a summary of no observations should mean, which is a
question about intent rather than parsing, and it was left open.

Skipping is also indiscriminate: a row dropped because of a typo and a row
dropped because the value is genuinely absent are counted identically, so
`metrics.skipped` signals that something was lost without saying what.

## Reproduction

```sh
ARCH_DATA_ROOT=data/public python eval.py
```

- Method: `eval.py`
- Notes: `attempts/robust-parse/`
- Development sample: `data/public/sample.csv`

The run writes `{score, metrics}` JSON to `$ARCH_EVAL_OUTPUT`; `metrics.n`
and `metrics.skipped` report how many rows contributed and how many were
dropped. To exercise the tolerant path, point `ARCH_DATA_ROOT` at a
directory whose `sample.csv` contains a blank or non-numeric `value` cell.
