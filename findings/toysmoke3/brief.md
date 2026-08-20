# Robust mean of a CSV column

## Problem

Computing the arithmetic mean of a numeric column in a CSV file is trivial
when every row is well-formed, but real files rarely are. A single blank or
non-numeric cell in the target column makes a naive reader raise partway
through and abort before producing any result — so one bad row costs you the
whole computation. The question here is whether the mean can be made robust to
such rows without changing the statistic being computed.

## Method

The reader parses the target `value` column one row at a time rather than in a
single bulk comprehension. Each cell is stripped of surrounding whitespace;
cells that are empty, or that fail to convert to a floating-point number, are
skipped and tallied instead of aborting the run. The computation raises only
in the degenerate case where *no* row parses at all, on the view that an
entirely unreadable file is a genuine error rather than something to average
over silently.

The statistic itself is unchanged: the reported value is the direct arithmetic
mean, `sum(values) / len(values)`, taken over exactly the rows that parsed. The
number of skipped rows is retained alongside the result as a diagnostic, so a
caller can tell how much of the input was discarded.

## Result

On the sample dataset — five rows with the values 1 through 5 — the method
returns a mean of **3.0** with zero rows skipped, identical to the naive
computation. This confirms the hardening is a no-op on well-formed input: it
adds robustness without perturbing the answer.

On a synthetic file with a blank row and a non-numeric row (`abc`) injected
among the same five values, the method again returns **3.0**, now reporting
**one** skipped row. The CSV layer absorbs the fully blank line before it
reaches the parser, and the explicit guard catches the non-numeric cell. The
crash path is closed in practice, not merely in principle, and the discarded
rows leave the mean unaffected.

## Limitations

The skip logic has no threshold: a file that is almost entirely malformed still
returns a mean over the small fraction that happened to parse, rather than
failing loudly. A stricter variant would reject inputs whose skip ratio exceeds
some bound instead of only failing on a 100%-unparseable file.

## Reproduction

With the repository's sample data, run the eval and read the mean from its
output:

```
ARCH_DATA_ROOT=data/public ARCH_EVAL_OUTPUT=/tmp/out.json python eval.py
cat /tmp/out.json
```

The method lives in `eval.py`; supporting notes are in
`attempts/robust-csv/RESEARCH_LOG.md`.
