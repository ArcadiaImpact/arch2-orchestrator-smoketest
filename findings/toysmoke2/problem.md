# toysmoke2 — Problem definition

_External-facing problem statement for the automated-research task
`arch/toysmoke2`. Pre-results companion to the wrap-up report at
`findings/toysmoke2/report.html` and to each top-ranked attempt's own
`findings/toysmoke2/brief.md`, committed to that attempt's own PR
branch. Anyone evaluating the validity and impact of the method or the
proposed approach should read this document first._

## Preliminary context

**This is not a research task.** It is a throwaway smoke test of the ARCH 2.0
orchestrator-pod feature, run against real RunPod and GitHub Actions
infrastructure. Read the "research question" below as a fixture, not as a
question anyone wants the answer to.

The thing actually under test is the ARCH 2.0 run lifecycle. Every ARCH run
before the orchestrator pod put supervision inside the researcher's own
session, which meant a run only advanced while a human — or a foreground
agent — was watching it. Moving supervision onto a cheap CPU pod is what makes
a genuinely unattended run possible. The open question is narrow and
engineering-shaped: does that handoff hold up on live infrastructure, rather
than in tests?

A first toy run (`arch/toysmoke`, 2026-08-19) established the basic answer —
the orchestrator pod booted, supervised a worker fleet, intervened, and
wrapped up. This second run is a deliberate re-run of that same task,
targeting three specific things changed since:

1. **The fixed wrap-up trigger** — whether wrap-up now fires autonomously at
   the wall-clock deadline, rather than needing a nudge.
2. **Transcript hashing** — whether worker transcripts are hashed and
   accounted for correctly.
3. **The leaderboard tie-break** — whether ranking is stable and deterministic
   when several attempts score identically. That case is not hypothetical
   here: in the prior run **all six attempts scored exactly 20.0**, so this
   task reliably produces the exact degenerate input the tie-break exists to
   handle.

That last point is why the task is being re-run *unchanged* rather than
replaced with something more interesting. The same six research directions are
seeded again (see below), so this run's leaderboard is directly comparable to
the previous one, and an all-ties leaderboard is guaranteed rather than hoped
for.

A mean-of-a-CSV task is a useful vehicle precisely because it is
uninteresting. The eval runs in milliseconds, needs no GPU, model, or network,
and has one unambiguous correct answer. Nothing about the science can mask a
failure: anything that goes wrong during this run is a failure of the
orchestration machinery, not of the task. The wall-clock budget is set to
**0.2 hours (12 minutes)** for the same reason — long enough for a worker to
open real scored attempts, short enough that the deadline-triggered wrap-up
path is exercised promptly instead of hours later.

No Slack or Drive context exists for this task. The context above was
synthesised from this repository's `README.md` and `eval.py`, from the prior
`arch/toysmoke` run's artifacts, and from the researcher's initialization
interview.

## Problem description

Toy smoke test #2 of the ARCH orchestrator pod (fleet launch/monitor separation) — validating the fixed wrap-up trigger, transcript-hashing, and leaderboard tie-break.

**Iteration data.** Workers iterate against `data/public`.
This is the public surface — anything that overfits to it without
transferring to the held-out surface scores worse, not better.

**Held-out data.** The authoritative eval runs against held-out data
that workers cannot see. Held-out identity (model, dataset shape, exact
metric breakdown) is deliberately hidden — only the score and the
researcher-whitelisted public metrics are surfaced on PR comments.

**Submissions.** Workers open labeled pull requests; each PR is one
attempt. The full attempt history (open + closed) is the contribution,
not just the winner — informative dead-ends are preserved.

## How we measure progress

The eval invocation:

```sh
python3 eval.py
```

It runs against `ARCH_DATA_ROOT` (= public path for workers, held-out
path for CI) and writes `{score, metrics}` JSON to `$ARCH_EVAL_OUTPUT`.
Same code in both places — only the data root switches.

**Publicly visible after each held-out run:**

- `score` (always)
- (no additional metric keys whitelisted — only the score)

Everything else stays inside the held-out pod and is wiped on
self-termination. This asymmetry is intentional: it lets workers iterate
against a real signal without enabling them to overfit to the held-out
distribution.

**The score is treated as an imperfect proxy, not an objective to maximize.**
It gives weak guidance on which directions are worth pursuing further —
nothing more. The worker fleet is instructed to prioritize genuine
scientific progress on the question above over pushing the number up
for its own sake; see "Why this measurement makes sense" below for what
the score does, and does not, capture.

## Why this measurement makes sense

Be clear about what the score is for here, because it is unusual: **the score
is not a proxy for research progress. It is an infrastructure assertion.**

The public sample has values 1–5 and means **3.0**. The held-out sample has
values 10, 20, 30 and means **20.0**. Those two numbers are deliberately far
apart and the held-out one is unguessable from the public one. So a posted
score of `20.0` is a single observable that simultaneously proves:

- the held-out network volume was created, populated, and mounted into the
  eval pod at `/mnt/arch_data`;
- the eval pod cloned the PR head, restored the trusted scoring paths from the
  base branch, and ran the researcher's own scorer against held-out data
  rather than the in-repo public reference;
- the score was posted back to the correct PR under the correct credentials.

Any *other* value falsifies exactly one of those. A score of `3.0` means the
volume was missing and the pod silently fell back to the in-repo reference
data (the pod labels that case "provisional"). A `null` score means the eval
crashed. Silence means the pod died before posting. This is why the eval is
deliberately trivial: it makes the number diagnostic of the pipeline rather
than of the method.

**What the score does not capture — and here that is nearly everything.** The
correct answer is already known, fixed, and identical for every reasonable
approach. There is no headroom: the arithmetic mean, a trimmed mean, the
median, a hardened parser, compensated summation, and `Decimal` arithmetic all
return 20.0 on a three-row symmetric sample. The score therefore carries
**zero signal about the quality of an attempt**. It cannot distinguish a
careful attempt from a careless one, and improving it is not possible.

Two consequences follow, and they are the point of the exercise rather than a
caveat on it:

1. **The leaderboard is expected to be entirely tied**, which is what makes
   this a real test of the tie-break rule this run exists to validate.
2. **Attempt quality has to be judged on the written artifact** — the PR body
   and `RESEARCH_LOG.md` — because the metric cannot judge it. The worker
   fleet is instructed accordingly: ship small, clearly-reasoned, honestly
   reported attempts, and do not chase a number that cannot move.

The triangulating measurements for this run are not in the headline score at
all. They are the orchestration observables: whether wrap-up fires on its own
at the 12-minute deadline, whether transcript hashes are recorded, and whether
the wrap-up ranking of six identical scores is stable and explainable. Those
are read from the run's own artifacts after the fact, not from the eval.

## Hypothesis space seeded into the worker fleet

The research directions below were seeded into worker pods at
initialization. They are not exhaustive — workers also propose their
own — but they cover the priors the researcher started with, plus (if
applicable) paper-grounded directions surfaced during init.

1. Arithmetic mean baseline — verify the direct `sum(values) / len(values)` computation end to end, and confirm it is the reference every other direction is compared against.

2. Trimmed mean — drop the extreme values before averaging, and compare against the arithmetic mean baseline.

3. Median — use the median instead of the mean, and characterise where the two diverge.

4. Robust CSV parsing — harden the reader so a malformed, blank, or non-numeric row cannot crash the eval.

5. Compensated summation — use `math.fsum` (or Kahan summation) so floating-point error does not accumulate across the sum.

6. Decimal arithmetic — compute the mean with `decimal.Decimal` for exact base-10 arithmetic, and compare against the binary-float result.


## Reproduction

- Branch: `arch/toysmoke2` on the project repo.
- Eval shim: `.arch/eval.sh` — same script runs on workers (public
  data) and in CI (held-out data); only `ARCH_DATA_ROOT` differs.
- Worker fleet: scaffolded by `arch init` and spawned by `arch run` with the
  wall-clock budget set at init time (0.2h for this run). `arch monitor`
  reports live fleet health; `arch findings` reports the current leaderboard.

Each top-ranked attempt's own brief (`findings/toysmoke2/brief.md`,
committed to that attempt's PR branch at wrap-up) states the problem, the
method that was built, and the scientific result, with a minimal
reproduction appendix — written to read as a standalone summary of that one
attempt, not a narration of the iteration process. The wrap-up report at
`findings/toysmoke2/report.html` (on the task branch) ranks the top
attempts against each other and links to each one's PR and brief.
