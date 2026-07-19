# Pre-commitment: Qwen3 v1 held-out test

**Written after rejecting priority prompt v2 and before making any held-out
model request.**

## Decision

Does Qwen3 4B with the original prompt qualify for a small offline prototype
that proposes ticket routing to a human reviewer?

A pass does not authorize autonomous routing, customer-facing responses, or
production use. It supports only a shadow-mode prototype in which a person
reviews every prediction.

## Candidate selection

- Candidate: `qwen3:4b`, Ollama ID `359d7dd4bcda`
- Quantization: Q4_K_M
- Prompt: `evals/support_triage/prompt.txt`
- Prompt SHA-256:
  `9e1afd232a800aefb723984684d1b1aefc677a730feda13023c4d04b09f22f7b`
- Runtime: Ollama 0.32.1
- Hardware: Apple M1 Pro with 16 GB memory

Qwen3 is the only held-out candidate because it passed the development gate:
100% valid schema, 94.7% escalation recall, and 72.5% exact match. Gemma 3 4B
did not pass and will not consume the held-out split in this cycle.

## Product behavior

- Unit: one fictional English-language support ticket
- Intended use: offline routing proposal reviewed by a human
- Excluded uses: autonomous action, automatic escalation closure, support
  replies, safety-critical decisions, and claims of production reliability
- Most costly false positive: unnecessary human escalation and slower handling
- Most costly false negative: failing to surface a compromised account,
  disputed charge, outage, privacy request, or missing data

## Data

- Dataset: `evals/support_triage/dataset.jsonl`
- Dataset SHA-256:
  `d299f565faf9c7249e5164d75f16cd4f5be781235556fc108bbf7cbf3b5522c9`
- Development examples: 40, already used for model and prompt selection
- Held-out examples: 20, not previously sent to either model
- Source: fictional, manually reviewed, public synthetic tickets under the
  repository license
- Known gaps: English only; small sample; fictional traffic; public labels;
  no multi-turn, adversarial, multilingual, or real-distribution coverage

## Pre-committed held-out gate

| Metric | Threshold | Product rationale |
|---|---:|---|
| Valid-schema rate | at least 95% | Downstream software must parse predictions. |
| Escalation recall | at least 90% | Missing human-action cases is the highest-cost broad failure. |
| Exact match | at least 70% | Routing, priority, and escalation must work together. |
| `risk` slice escalation accuracy | 100% | Explicit risk cases must reach a human in this small set. |
| Median end-to-end latency | at most 60 seconds | Slow is tolerable offline; unbounded waiting is not. |

If the test set has no `risk` examples, that slice gate is **not evaluated** and
cannot be counted as a pass. All other thresholds still apply.

## Decision rule

- Pass every evaluated threshold: proceed to a small shadow-mode prototype with
  human review and collect a larger representative dataset.
- Miss any evaluated threshold: reject the prototype claim and return to data,
  policy, or model selection without retuning on the held-out examples.

Do not change labels, thresholds, prompt text, parsing, scoring, model settings,
or the candidate after seeing the test output. Do not rerun a failed example.

## Experiment controls

- Temperature 0 and Ollama JSON mode
- One sequential run
- No retries beyond the existing request behavior
- Same runner, scorer, runtime, hardware, and model revision as development
- No prompt v2 text

## Command

```bash
python3 run_eval.py \
  --models qwen3:4b \
  --split test \
  --prompt evals/support_triage/prompt.txt \
  --output-dir results/heldout-v1
```

## Interpretation limits

Twenty public synthetic examples cannot establish production reliability or a
stable population estimate. The result is a disciplined project milestone and
a regression reference, not a general leaderboard score.

## Results recorded after the run

The candidate failed the frozen gate and is rejected for the stated prototype.

| Metric | Threshold | Result | Outcome |
|---|---:|---:|:---:|
| Valid-schema rate | at least 95% | 100.0% | PASS |
| Escalation recall | at least 90% | 90.0% | PASS |
| Exact match | at least 70% | 60.0% | **FAIL** |
| `risk` slice escalation accuracy | 100% | 100.0% (n=2) | PASS |
| Median end-to-end latency | at most 60s | 36.83s | PASS |

The run was performed once with no retries. See the
[full held-out decision](../results/published/2026-07-18-qwen3-v1-held-out/README.md)
and raw result.

**Decision:** do not proceed to the shadow-mode prototype. The test split is
now consumed and becomes a public regression set.
