# Mean of a tabular sample, computed and independently verified

## Problem

Given a CSV file with a `value` column, report the arithmetic mean of that
column. The question is narrow and has a single defensible answer: the mean
of a finite set of numbers is fully determined by the data, so there is no
estimator to tune and no modelling choice to make. What is worth
establishing is that the computation is correct, and that its correctness
can be checked by someone other than the person who wrote it — the value is
consumed downstream, so a silent arithmetic or parsing error would
propagate without any obvious symptom.

## Method

The mean is computed directly: read the CSV with a header-aware reader,
convert each row's `value` cell to a float, and divide the sum of those
values by their count. No rows are filtered, no weighting is applied, and
no trimming or outlier handling is involved — the plain arithmetic mean
over every row present.

Because the primary computation is only three lines, the substantive part
of the work is the check on it rather than the computation itself.
`attempts/arithmetic-mean/verify_mean.py` is a standalone reimplementation
that re-reads the same CSV from the data root given by `ARCH_DATA_ROOT` and
recomputes the mean independently, printing the result. It shares no code
with the main path, so agreement between the two is a genuine
cross-check — a transcription error, an off-by-one in the row count, or a
column misread would show up as a disagreement rather than passing
unnoticed.

## Result

On the development sample (`data/public/sample.csv`, values 1 through 5),
the mean is 3.0, and the independent reimplementation reproduces that value
exactly. Run against a separate evaluation sample that was not available
during development, the same computation returns a mean of 20.0.

The two implementations agree on every input tried, which is the intended
outcome: it establishes that the reported figure reflects the data rather
than an artifact of one particular implementation. It is worth being clear
about what this does *not* show. Agreement between two implementations of
the same formula rules out transcription and parsing mistakes; it cannot
rule out a shared misunderstanding of which quantity was wanted in the
first place. If the intended statistic were something other than the
unweighted mean over all rows, both implementations would be wrong
together and this check would not catch it.

## Limitations

Every row is treated as valid input. A blank or non-numeric `value` cell
raises during conversion rather than being skipped, so the method assumes a
clean, fully-populated column. Both samples used here satisfy that
assumption, so the behaviour on malformed input is untested in practice.

## Reproduction

```sh
ARCH_DATA_ROOT=data/public python attempts/arithmetic-mean/verify_mean.py
```

- Method and verification script: `attempts/arithmetic-mean/`
- Development sample: `data/public/sample.csv`

Point `ARCH_DATA_ROOT` at any directory containing a `sample.csv` with a
`value` column to reproduce the figure for that sample.
