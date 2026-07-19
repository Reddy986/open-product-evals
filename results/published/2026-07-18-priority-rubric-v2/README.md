# Rejected experiment: priority rubric v2

- **Run date:** July 18, 2026
- **Evaluation split:** development (40 synthetic tickets)
- **Changed variable:** priority-rule wording only
- **Decision:** reject prompt v2 and retain prompt v1

## Hypothesis

The original prompt did not explicitly say that a ticket can require human
action without being high priority. Prompt v2 added a priority decision order
and separated priority from escalation. The hypothesis was that this would
reduce priority errors without harming routing, escalation, or JSON reliability.

The [adoption rule](../../../experiments/2026-07-18-priority-rubric-v2.md)
was published in draft PR #3 before either model saw prompt v2.

## Result

| Model | Metric | Prompt v1 | Prompt v2 | Delta |
|---|---|---:|---:|---:|
| Gemma 3 4B | Priority accuracy | 60.0% | 50.0% | -10.0 pp |
| Gemma 3 4B | Exact match | 60.0% | 40.0% | -20.0 pp |
| Gemma 3 4B | Escalation recall | 89.5% | 52.6% | -36.9 pp |
| Gemma 3 4B | Valid schema | 100.0% | 100.0% | 0.0 pp |
| Qwen3 4B | Priority accuracy | 77.5% | 75.0% | -2.5 pp |
| Qwen3 4B | Exact match | 72.5% | 67.5% | -5.0 pp |
| Qwen3 4B | Escalation recall | 94.7% | 89.5% | -5.2 pp |
| Qwen3 4B | Valid schema | 100.0% | 97.5% | -2.5 pp |

Prompt v2 violated every no-regression condition. It is rejected even though it
fixed individual examples.

## Paired prediction changes

| Model | Exact improvements | Exact regressions | Priority improvements | Priority regressions | Escalation improvements | Escalation regressions |
|---|---:|---:|---:|---:|---:|---:|
| Gemma 3 4B | 2 | 10 | 3 | 7 | 2 | 7 |
| Qwen3 4B | 7 | 9 | 6 | 7 | 2 | 3 |

The paired view explains why inspecting only a few hand-picked wins would have
been misleading. Qwen3 corrected the unrecognized-charge priority, the
euro-receipt category, and several boundary priorities, but it introduced more
total exact-match regressions than improvements.

## Failure mechanism

The sentence separating priority from escalation was directionally sound but
too easy to overgeneralize:

- Gemma 3 changed seven previously correct escalation decisions to false,
  including refunds, incorrect charges, ownership changes, crashes, stuck
  exports, and disconnected integrations.
- Qwen3 corrected six priority labels but regressed seven others, added three
  escalation regressions, and returned one invalid schema.
- Both models also changed category decisions even though the category section
  was byte-for-byte unchanged. Prompt sections are not behaviorally isolated.

This is the central lesson: more explicit policy text does not guarantee better
behavior in a small model. Negative wording about one field can leak into other
fields, so prompt changes need end-to-end regression gates.

## Reproduction

```bash
python3 run_eval.py \
  --models gemma3:4b qwen3:4b \
  --split development \
  --prompt evals/support_triage/prompt_v2.txt
```

- Dataset SHA-256:
  `d299f565faf9c7249e5164d75f16cd4f5be781235556fc108bbf7cbf3b5522c9`
- Prompt v1 SHA-256:
  `9e1afd232a800aefb723984684d1b1aefc677a730feda13023c4d04b09f22f7b`
- Prompt v2 SHA-256:
  `110d4bb03f679b3f9c3e80e61ce1680bd3864c903f36423b440c53801d00e3d9`
- Runtime and hardware: Ollama 0.32.1 on an Apple M1 Pro with 16 GB memory
- Sampling: temperature 0, one sequential run per model

Artifacts:

- [Generated v2 model comparison](comparison.md)
- [Gemma 3 raw v2 result](gemma3-4b-development.json)
- [Qwen3 raw v2 result](qwen3-4b-development.json)
- [Prompt v1 results](../2026-07-18-open-model-comparison/README.md)

## Next decision

Retain prompt v1. Do not tune another prompt against the same 40 examples in
this cycle. Freeze the v1 prompt, labels, model revision, and product gate, then
run the held-out split once for the Qwen3 quality candidate.
