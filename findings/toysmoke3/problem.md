# toysmoke3 — Problem definition

_External-facing problem statement for the automated-research task
`arch/toysmoke3`. Pre-results companion to the wrap-up report at
`findings/toysmoke3/report.html` and to each top-ranked attempt's own
`findings/toysmoke3/brief.md`, committed to that attempt's own PR
branch. Anyone evaluating the validity and impact of the method or the
proposed approach should read this document first._

## Preliminary context

**This is not a research task.** It is a throwaway smoke test of the ARCH 2.0
orchestrator-pod feature (ArcadiaImpact/arch2#136), run against live RunPod and
GitHub Actions infrastructure. The "research question" is deliberately trivial
so that nothing about the science can obscure what is actually being tested:
whether the CPU orchestrator pod boots, supervises a worker fleet, intervenes
when a worker stalls, and triggers wrap-up autonomously at the deadline.

The broader thing being validated is the arch2 lifecycle itself. Every arch2 run
before the orchestrator pod put supervision inside the researcher's own session,
which meant a run only progressed while a human — or a foreground agent — was
watching it. Moving supervision onto a cheap CPU pod is what makes a genuinely
unattended run possible. The open question is not whether that design is sound
in principle, but whether the handoff survives contact with live infrastructure.

This run is the **third** pass over the same toy task, after `arch/toysmoke` and
`arch/toysmoke2`. Re-running an already-solved task is the point rather than a
limitation: because the correct answer, the direction list, and the expected
leaderboard shape are all known in advance from the previous two runs, any
difference observed this time is attributable to the orchestration machinery and
not to the task. Three specific mechanisms are under test on this pass — the
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

No Slack or Drive context was pulled for this task — none exists. The context
above was lifted from local notes in this repository: its `README.md`, and the
problem definition and configuration committed by the two prior runs on the
`arch/toysmoke` and `arch/toysmoke2` branches.

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

Be explicit about what the number means here: **the score is not a research
signal at all.** The arithmetic mean of a three-row CSV has exactly one correct
value, so the score cannot rank a better method above a worse one — every
correct attempt lands on 20.0 and every incorrect one does not. There is no
hypothesis space to explore and no progress to make. Do not read this run's
leaderboard as a comparison of methods.

What the score *is* a proxy for is **the health of the pipeline that produced
it**. A non-null 20.0 posted on a PR is a compact end-to-end assertion that all
of the following worked: the PR carried this run's label
(`arch/toysmoke3-<run_id>`); the `pull_request` workflow fired from the task base
branch; the held-out eval pod was scheduled in EU-RO-1 and got real hardware; it
cloned the PR head with the durable worker token; it restored the trusted scoring
paths from the base branch so the PR could not alter its own scorer; the network
volume mounted and carried the held-out CSV; the eval ran; and the sanitized
result posted back through the publish allow-list. That chain — not the
arithmetic — is the thing under test, and it is why this task keeps a held-out
split it does not scientifically need.

What the score deliberately does **not** capture is nearly everything this smoke
test actually cares about: whether the orchestrator pod stayed alive for the full
budget, whether it detected and intervened on a stalled worker, whether the
wrap-up trigger fired at the deadline without a human, whether transcript-hashing
produced stable digests, whether the leaderboard tie-break ordered a fully-tied
board deterministically, and whether cost stayed bounded. Those are the real
measurements of this run. They are observed directly — from the orchestrator's
own dashboard and report, from `arch monitor`, from the wrap-up artifacts, and
from the RunPod console — and never inferred from the score.

Two specific misreadings to guard against, both seen before. A score of **3.0**
on a held-out PR does not mean a worse method; it means the held-out volume did
not mount and the pod silently fell back to the in-repo public reference. The
eval "succeeded" but the number is provisional and the held-out path is broken —
the startup script labels this case explicitly, and that label is the thing to
read, not the number. A **null** score means the pod died before posting, which
the PR itself cannot distinguish from "still running" — so pod health is watched
over SSH throughout, not inferred from the absence of a comment.

There is no secondary or qualitative measurement of the *task*, and none is
needed: the correct answer is known in advance, which is the entire reason this
task was chosen. The triangulating measurements are all measurements of the
orchestrator, listed above.

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

- Branch: `arch/toysmoke3` on the project repo.
- Eval shim: `.arch/eval.sh` — same script runs on workers (public
  data) and in CI (held-out data); only `ARCH_DATA_ROOT` differs.
- Worker fleet: spawned by `arch init` with the wall-clock budget set at
  that time. `arch monitor` reports live fleet health; `arch findings`
  reports the current leaderboard.

Each top-ranked attempt's own brief (`findings/toysmoke3/brief.md`,
committed to that attempt's PR branch at wrap-up) states the problem, the
method that was built, and the scientific result, with a minimal
reproduction appendix — written to read as a standalone summary of that one
attempt, not a narration of the iteration process. The wrap-up report at
`findings/toysmoke3/report.html` (on the task branch) ranks the top
attempts against each other and links to each one's PR and brief.
