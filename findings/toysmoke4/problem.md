# toysmoke4 — Problem definition

_External-facing problem statement for the automated-research task
`arch/toysmoke4`. Pre-results companion to the wrap-up report at
`findings/toysmoke4/report.html` and to each top-ranked attempt's own
`findings/toysmoke4/brief.md`, committed to that attempt's own PR
branch. Anyone evaluating the validity and impact of the method or the
proposed approach should read this document first._

## Preliminary context

**This is not a research task.** It is a throwaway smoke test of the ARCH 2.0
CPU-orchestrator-pod feature (ArcadiaImpact/arch2#136), run against live RunPod
and GitHub Actions infrastructure. The "research question" is deliberately
trivial so that nothing about the science can obscure what is actually being
tested: whether the CPU orchestrator pod boots, supervises a worker fleet,
intervenes when a worker stalls, and triggers wrap-up autonomously at the
deadline.

The broader thing being validated is the arch2 lifecycle itself. Every arch2 run
before the orchestrator pod put supervision inside the researcher's own session,
which meant a run only progressed while a human — or a foreground agent — was
watching it. Moving supervision onto a cheap CPU pod is what makes a genuinely
unattended run possible. The open question is not whether that design is sound
in principle, but whether the handoff survives contact with live infrastructure.

This run is the **fourth** pass over the same toy task, after `arch/toysmoke`,
`arch/toysmoke2`, and `arch/toysmoke3`. Re-running an already-solved task is the
point rather than a limitation: because the correct answer, the direction list,
and the expected leaderboard shape are all known in advance from the previous
three runs, any difference observed this time is attributable to the
orchestration machinery and not to the task. The direction list below is
deliberately identical to the one seeded in those runs, so the leaderboard shape
is comparable across passes. Three specific mechanisms are under test here — the
fixed wrap-up trigger, transcript-hashing, and the leaderboard tie-break — and
the tie-break in particular is only exercisable *because* the task is degenerate:
every correct attempt scores identically, so the entire leaderboard is one large
tie and the tie-break code path is guaranteed to run.

A mean-of-a-CSV task is a useful vehicle for the same reason it is a useless
research question. The eval is pure-stdlib Python, runs in well under a second,
needs no GPU, no model, and no dependency install, and has an unambiguous correct
answer. That makes the wall-clock budget for this run — 12 minutes — sufficient,
and it means a failure observed during the run is a failure of orchestration
rather than of the science. The public/held-out split (public mean 3.0, held-out
mean 20.0) is retained solely so the held-out path is genuinely exercised: a
worker reading the public sample cannot guess the held-out answer, so a posted
score of 20.0 is positive evidence that the network volume mounted and the
authoritative scorer ran.

No Slack or Drive context was pulled for this task — none exists, and neither
integration was reachable from the init session. The context above was lifted
from local notes in this repository: its `README.md`, and the problem definitions
and configuration committed by the three prior runs on the `arch/toysmoke`,
`arch/toysmoke2`, and `arch/toysmoke3` branches.

## Problem description

Toy smoke test #4 of the ARCH orchestrator pod (fleet launch/monitor separation) — validating the fixed wrap-up trigger, transcript-hashing, and leaderboard tie-break.

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

Be explicit about what the number is for here, because this task inverts the
usual relationship between score and research progress.

**What the score is a proxy for.** In a real ARCH task, the held-out score
proxies the quality of a method. Here it proxies something much narrower:
*whether the held-out evaluation path executed correctly end to end.* The public
sample means 3.0 and the held-out sample means 20.0, and a worker can only ever
see the former. So a posted score of **20.0** is direct evidence that a chain of
independent components all worked — a labeled PR fired the GitHub Actions
workflow, the workflow spawned a RunPod pod in the datacenter pinned by the
network volume, the pod cloned the PR head with a durable token, the volume
mounted at `/mnt/arch_data`, the trusted scorer was restored from the base branch
rather than taken from the PR, the eval ran, and the sanitized result was posted
back to the PR. A score of **3.0** is equally informative in the negative
direction: it means the volume did not mount and the pod silently fell back to
the in-repo public reference. A **null** or absent score means the pod died
before posting. The score is a three-way diagnostic of the infrastructure, not a
measure of anything scientific.

**Why improving it does not mean progress.** 20.0 is the ceiling, and *any*
correct implementation of "mean of a column" reaches it on the first try. The
arithmetic mean, the trimmed mean, the median, an `fsum`-compensated mean, and a
`Decimal` mean all return exactly 20.0 on the held-out data, because the held-out
sample (10, 20, 30) is symmetric and exactly representable in binary floating
point. There is therefore no score gradient to climb and no scientific ranking to
recover from the leaderboard. This is intentional: the resulting all-way tie is
precisely what exercises the leaderboard tie-break code path this run is meant to
validate. Treating a 20.0 as "a good attempt" would be a category error — it
means the plumbing worked.

**What the score does not capture.** Essentially everything this run actually
cares about. The score says nothing about whether the orchestrator pod booted,
whether it detected and intervened on a stalled worker, whether transcript
hashing produced stable digests, whether the wrap-up trigger fired at the
12-minute deadline without a human, or whether pods self-terminated instead of
billing on. Those are the real observables, and they are read from the
orchestrator's own dashboard and logs, from `arch monitor`, and from the wrap-up
report — not from any PR comment. The score also cannot distinguish a genuinely
robust implementation from a fragile one: the "robust CSV parsing" direction, for
instance, is only meaningfully different from the baseline on malformed input,
and the held-out file is clean, so both score identically.

**Triangulating measurements.** Because the headline score is deliberately
uninformative, judge this run against: the orchestrator pod's supervision log and
dashboard; `arch monitor` fleet health during the 12-minute window; the presence
of a distinct, non-duplicative attempt per direction with a readable
`RESEARCH_LOG.md`; whether wrap-up produced a ranked leaderboard with a
deterministic tie-break; and whether every pod was reaped at the end. A run in
which every PR scores 20.0 but the orchestrator never triggered wrap-up is a
failed run, and a run in which the fleet only managed one attempt but the full
lifecycle completed unattended is a successful one.

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

- Branch: `arch/toysmoke4` on the project repo.
- Eval shim: `.arch/eval.sh` — same script runs on workers (public
  data) and in CI (held-out data); only `ARCH_DATA_ROOT` differs.
- Worker fleet: spawned by `arch init` with the wall-clock budget set at
  that time. `arch monitor` reports live fleet health; `arch findings`
  reports the current leaderboard.

Each top-ranked attempt's own brief (`findings/toysmoke4/brief.md`,
committed to that attempt's PR branch at wrap-up) states the problem, the
method that was built, and the scientific result, with a minimal
reproduction appendix — written to read as a standalone summary of that one
attempt, not a narration of the iteration process. The wrap-up report at
`findings/toysmoke4/report.html` (on the task branch) ranks the top
attempts against each other and links to each one's PR and brief.
