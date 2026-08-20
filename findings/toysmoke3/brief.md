# Robust CSV parsing for the mean computation

## Problem

The task is to compute the arithmetic mean of a column of numeric values read
from a CSV file. A real-world reader has to tolerate imperfect input: blank
cells, rows missing the expected column, and cells holding non-numeric text.
The question is whether the mean computation can be made resilient to such rows
without changing the answer it produces on clean data.

## Method

Parsing is isolated into a `load_values()` helper. It iterates the rows of the
CSV, skips any row whose `value` field is missing or blank, and wraps the
numeric conversion in a guard that discards a cell it cannot parse as a float,
counting it as skipped rather than raising. The well-formed values are then
averaged as `sum(values) / len(values)`. When no row yields a numeric value,
the computation returns an explicit "no numeric rows found" result instead of
dividing by zero.

## Result

On the reference sample (values 1 through 5) the hardened reader parses every
row, skips none, and reports a mean of 3.0 — identical to the unhardened
computation and to the published reference value. The change is therefore a
no-op on clean input: it adds resilience to malformed rows without perturbing
the result.

## Limitations

The reference data contains no malformed rows, so the skip-and-count path is
covered by the guard logic but not exercised against real corruption by this
dataset.

## Reproduction

Run the eval against the public data in the current revision of this repo. The
method lives in `attempts/robust-parse/`, with the parsing helper in `eval.py`.
