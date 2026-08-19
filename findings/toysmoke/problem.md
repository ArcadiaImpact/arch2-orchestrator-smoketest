# toysmoke — Problem definition

_External-facing problem statement for the automated-research task
`arch/toysmoke`. Pre-results companion to the wrap-up report at
`findings/toysmoke/report.html` and to each top-ranked attempt's own
`findings/toysmoke/brief.md`, committed to that attempt's own PR
branch. Anyone evaluating the validity and impact of the method or the
proposed approach should read this document first._

## Preliminary context

**This is not a research task.** It is a throwaway smoke test of the ARCH 2.0
orchestrator-pod feature (ArcadiaImpact/arch2 PR #136), run against real
RunPod and GitHub Actions infrastructure. The "research question" is
deliberately trivial so that nothing about the science can obscure what is
actually being tested: whether the orchestrator pod boots, supervises a
worker fleet, intervenes when a worker stalls, and triggers wrap-up
autonomously at the deadline.

The broader thing being validated is the arch2 lifecycle itself. Every
previous arch2 run put supervision in the researcher's own session — which
meant the run only progressed while a human (or a foreground agent) was
watching it. Moving supervision onto a CPU pod is what makes a genuinely
unattended run possible, and the open question is simply whether that
handoff works end to end on live infrastructure rather than in tests.

A mean-of-a-CSV task is a useful vehicle precisely because it is
uninteresting: the eval runs in milliseconds, has no GPU or model
dependencies, and has an unambiguous correct answer, so any failure observed
during the run is a failure of the orchestration machinery and not of the
task. The public/held-out split (public mean 3.0, held-out mean 20.0) is
retained only so the held-out path is genuinely exercised — a worker that
reads the public sample cannot guess the held-out answer, so a held-out
score of 20.0 is positive evidence that the volume mounted and the
authoritative scorer ran.

No external context was pulled for this task (no Slack, Drive, or local
notes) — there is none to pull.

## Problem description

Compute the mean of values in sample.csv. Trivial baseline: scores 3.0 against public data, 20.0 against held-out data.

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
python eval.py
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
signal at all.** The arithmetic mean of a three-row CSV has exactly one
correct value, so the score cannot distinguish a better method from a worse
one — every correct attempt lands on 20.0 and every incorrect one does not.
There is no hypothesis space to explore and no progress to make.

What the score *is* a proxy for is **the health of the pipeline that
produced it**. A non-null 20.0 posted on a PR is a compact end-to-end
assertion that all of the following worked: the PR carried the run label; the
`pull_request` workflow fired from the task base branch; the held-out eval pod
was scheduled in EU-RO-1 and got real hardware; it cloned the PR head with the
worker token; it restored the trusted scoring paths from the base branch; the
network volume mounted and carried the held-out CSV; the eval ran; and the
sanitized result posted back through the publish allow-list. That chain — not
the arithmetic — is the thing under test.

What the score deliberately does **not** capture is everything this smoke test
actually cares about: whether the orchestrator pod stayed alive, whether it
detected and intervened on a stalled worker, whether it reaped pods and
triggered wrap-up at the deadline, and whether cost stayed bounded. Those are
observed directly from the orchestrator's dashboard and report, from
`arch monitor`, and from the RunPod console — never inferred from the score.

Two specific misreadings to guard against. A score of **3.0** means the
held-out volume did *not* mount and the pod fell back to the in-repo public
reference; the eval "succeeded" but the number is provisional and the held-out
path is broken. A **null** score means the pod died before posting, which the
PR itself cannot distinguish from "still running" — so pod health is watched
over SSH throughout, not inferred from the absence of a comment.

There is no secondary or qualitative measurement, and none is needed: the
correct answer is known in advance, which is the entire reason this task was
chosen.

## Hypothesis space seeded into the worker fleet

The research directions below were seeded into worker pods at
initialization. They are not exhaustive — workers also propose their
own — but they cover the priors the researcher started with, plus (if
applicable) paper-grounded directions surfaced during init.

1. Compute the arithmetic mean directly.

2. Try a trimmed/robust mean and compare.


## Reproduction

- Branch: `arch/toysmoke` on the project repo.
- Eval shim: `.arch/eval.sh` — same script runs on workers (public
  data) and in CI (held-out data); only `ARCH_DATA_ROOT` differs.
- Worker fleet: spawned by `arch init` with the wall-clock budget set at
  that time. `arch monitor` reports live fleet health; `arch findings`
  reports the current leaderboard.

Each top-ranked attempt's own brief (`findings/toysmoke/brief.md`,
committed to that attempt's PR branch at wrap-up) states the problem, the
method that was built, and the scientific result, with a minimal
reproduction appendix — written to read as a standalone summary of that one
attempt, not a narration of the iteration process. The wrap-up report at
`findings/toysmoke/report.html` (on the task branch) ranks the top
attempts against each other and links to each one's PR and brief.
