#!/bin/bash
# Eval shim — invokes the researcher's eval function with ARCH_DATA_ROOT.
# Writes the result as JSON to ARCH_EVAL_OUTPUT.
#
# Same shim runs in three places:
#   * `arch eval` on a worker pod (ARCH_DATA_ROOT = public path)
#   * `arch eval` on the researcher's laptop (ARCH_DATA_ROOT = public path)
#   * The held-out pod via CI (ARCH_DATA_ROOT = /mnt/arch_data)
#
# ----------------------------------------------------------------
# Output contract — your invocation MUST write this JSON to $ARCH_EVAL_OUTPUT:
#
#   {
#     "score":   <float | null>,        # required. higher is better.
#                                       # null means "not scored" (e.g. constraint
#                                       # violated, eval failed). `null` PRs
#                                       # are excluded from `arch findings`.
#     "metrics": <object | null>,       # required. component metrics. Anything
#                                       # in here is fair game for *internal*
#                                       # use; only keys listed in
#                                       # `[public_metrics]` in .arch/config.toml
#                                       # are surfaced on PR comments / check_runs.
#     "notes":   "<string>"             # optional. shown next to the score.
#   }
#
# Numeric gates: if you compare floats against a threshold (e.g. capability
# drop ≤ 5 pp), ROUND before the comparison. Python addition gives
# `5.000000000000004` from arithmetically-clean inputs and silently fails
# the gate. Always: `round(value, 2)` before the gate, and round again
# before serializing to JSON.
#
# LLM-judge evals: construct the Anthropic client FAIL-FAST, not with SDK
# defaults. The default is a 600s timeout × 3 retries (~30 min); under the
# API contention of a running fleet your eval will hang for half an hour per
# call before failing. Use a short budget and fall back to a deterministic
# score:
#
#   client = anthropic.Anthropic(timeout=150.0, max_retries=1)
#   try:
#       verdict = client.messages.create(...)
#   except (anthropic.APITimeoutError, anthropic.APIError):
#       verdict = deterministic_fallback()   # ~3 min, not ~30 min
# ----------------------------------------------------------------

set -euo pipefail

: "${ARCH_DATA_ROOT:?ARCH_DATA_ROOT must be set}"
: "${ARCH_EVAL_OUTPUT:?ARCH_EVAL_OUTPUT must be set}"

# Researcher-provided invocation. Substituted at `arch init` time.
python3 eval.py
