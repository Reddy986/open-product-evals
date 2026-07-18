# First open-model comparison: Qwen3 4B vs Gemma 3 4B

- **Run date:** July 18, 2026
- **Evaluation split:** development (40 synthetic tickets)
- **Decision status:** evidence for iteration, not a production approval

## Product question

Which small local model is the better candidate for a support-ticket triage
workflow when missed human escalations are costly, structured output is
required, and latency still matters?

## Result

| Candidate | Valid schema | Category accuracy | Priority accuracy | Escalation recall | Exact match | Median latency | Product gate |
|---|---:|---:|---:|---:|---:|---:|:---:|
| `qwen3:4b` | 100.0% | 97.5% | 77.5% | 94.7% | 72.5% | 34.05s | PASS |
| `gemma3:4b` | 100.0% | 92.5% | 60.0% | 89.5% | 60.0% | 1.64s | FAIL |

Qwen3 is the stronger **quality candidate** under the worked gate: at least
95% valid schema, 90% escalation recall, and 70% exact match. Gemma 3 is the
stronger **latency candidate**: its median response was about 21 times faster
on this machine.

The practical decision is to continue prompt and rubric work with Qwen3 as the
quality reference while keeping Gemma 3 as the latency baseline. Neither model
is approved for production use from this run. The prompt and gate should be
frozen before the held-out test split is run.

## What failed

- Both models returned valid JSON for all 40 tickets.
- Priority calibration caused most errors: 9 for Qwen3 and 16 for Gemma 3.
- Qwen3 missed one required escalation and added one unnecessary escalation.
- Gemma 3 missed two required escalations and added two unnecessary escalations.
- Some label disagreements expose rubric ambiguity rather than an obviously
  wrong model answer. For example, the expected priority for a future
  Salesforce integration is `medium`, while Qwen3 selected `low`.

That last point matters: error analysis should improve the labeling policy as
well as the prompt. A deterministic grader can be perfectly reproducible and
still encode a debatable product judgment.

## Reproduction

Both candidates received the same prompt, examples, temperature, JSON-output
constraint, and sequential request pattern.

```bash
ollama pull qwen3:4b
ollama pull gemma3:4b
python3 run_eval.py --models gemma3:4b qwen3:4b --split development
python3 compare_results.py results/gemma3-4b-development-*.json \
  results/qwen3-4b-development-*.json --output results/comparison.md
```

| Item | Value |
|---|---|
| Machine | Apple M1 Pro, 16 GB memory |
| Operating system | macOS 15.6.1 |
| Runtime | Ollama 0.32.1 |
| Qwen model | `qwen3:4b`, ID `359d7dd4bcda`, Q4_K_M, 4.0B parameters |
| Gemma model | `gemma3:4b`, ID `a2af6cc3eb7f`, Q4_K_M, 4.3B parameters |
| Dataset SHA-256 | `d299f565faf9c7249e5164d75f16cd4f5be781235556fc108bbf7cbf3b5522c9` |
| Prompt SHA-256 | `9e1afd232a800aefb723984684d1b1aefc677a730feda13023c4d04b09f22f7b` |
| Sampling | temperature 0, one run per model |

Artifacts:

- [Generated comparison](comparison.md)
- [Gemma 3 raw result](gemma3-4b-development.json)
- [Qwen3 raw result](qwen3-4b-development.json)

## Limitations

- This is a small, public, synthetic development set, not a
  contamination-resistant benchmark.
- The run has no repeated trials or confidence intervals.
- Latency is end-to-end sequential latency on one laptop, not a throughput or
  concurrency test. Qwen3 used its default thinking-capable behavior.
- Public model tags can change. The recorded Ollama IDs improve traceability,
  but long-term reproduction may require pinning model manifests.
- The product gate is a worked hypothesis, not a safety certification.
- Model licenses differ; model weights are not distributed in this repository.

## Next experiment

1. Tighten the priority rubric using development-set disagreements.
2. Change only one prompt or rubric variable at a time.
3. Freeze the prompt, labels, and gate.
4. Run the 20-example held-out test split once.
5. Add repeated trials and uncertainty estimates before making close calls.
