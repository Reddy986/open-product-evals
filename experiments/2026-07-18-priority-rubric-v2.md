# Pre-commitment: priority rubric v2

**Written before running prompt v2 on either model.**

## Decision

Should the support-triage evaluation adopt a more explicit priority rubric
before freezing the prompt and running the held-out test split?

## Why this variable

The first development run produced 16 priority errors for Gemma 3 4B and 9 for
Qwen3 4B. Failure review found a recurring ambiguity: a ticket may require a
human without being time-sensitive or high impact. The original prompt did not
explicitly separate priority from escalation.

## Candidate and baseline

- Candidate: `evals/support_triage/prompt_v2.txt`
- Candidate prompt SHA-256:
  `110d4bb03f679b3f9c3e80e61ce1680bd3864c903f36423b440c53801d00e3d9`
- Baseline: `evals/support_triage/prompt.txt`
- Baseline prompt SHA-256:
  `9e1afd232a800aefb723984684d1b1aefc677a730feda13023c4d04b09f22f7b`
- Models: `gemma3:4b` (`a2af6cc3eb7f`) and `qwen3:4b`
  (`359d7dd4bcda`)
- Quantization: Q4_K_M for both models
- Runtime: Ollama 0.32.1
- Hardware: Apple M1 Pro with 16 GB memory

## Data

- Dataset: `evals/support_triage/dataset.jsonl`
- Dataset SHA-256:
  `d299f565faf9c7249e5164d75f16cd4f5be781235556fc108bbf7cbf3b5522c9`
- Development examples: 40
- Held-out test examples: 20, not used in this experiment
- Source: fictional, manually reviewed, public synthetic tickets under the
  repository license

## Baseline development results

| Model | Priority accuracy | Escalation recall | Exact match | Valid schema |
|---|---:|---:|---:|---:|
| `gemma3:4b` | 60.0% | 89.5% | 60.0% | 100.0% |
| `qwen3:4b` | 77.5% | 94.7% | 72.5% | 100.0% |

## Adoption rule chosen before the run

Adopt prompt v2 only if all of the following are true on the development split:

1. neither model loses priority accuracy;
2. neither model loses exact-match accuracy;
3. neither model loses escalation recall or valid-schema rate; and
4. at least one model gains at least 5 percentage points of priority accuracy.

Otherwise retain prompt v1. A one-example change is 2.5 percentage points, so
the final requirement demands at least two additional correct priority labels
for one candidate rather than treating a single example as decisive.

## Experiment controls

- The only intended prompt change is the priority-rule section.
- Dataset, expected labels, categories, escalation policy, model tags,
  temperature, JSON mode, request order, runtime, and hardware stay fixed.
- One sequential run per model at temperature 0.
- The development split is used for prompt selection.
- The test split remains untouched until the prompt and gate are frozen.

## Command

```bash
python3 run_eval.py \
  --models gemma3:4b qwen3:4b \
  --split development \
  --prompt evals/support_triage/prompt_v2.txt
```

## Known limitations

- The priority labels encode a fictional product policy and remain debatable.
- The public synthetic dataset is small and not representative production
  traffic.
- A single temperature-zero run does not establish variance or confidence.
- The adoption rule prevents regression in two models but may reject a prompt
  that is beneficial for only one deployment target.
