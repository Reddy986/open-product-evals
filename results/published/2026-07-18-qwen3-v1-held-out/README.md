# Held-out decision: reject the Qwen3 v1 prototype claim

- **Run date:** July 18, 2026
- **Candidate:** Qwen3 4B, Q4_K_M, Ollama ID `359d7dd4bcda`
- **Evaluation split:** first and only held-out use of the 20 test tickets
- **Decision:** do not proceed to the proposed shadow-mode prototype

## Product claim tested

After Qwen3 passed the development gate, the experiment asked whether the same
frozen model and prompt qualified for an offline triage prototype in which a
human reviews every prediction. The gate was
[published before the run](../../../experiments/2026-07-18-qwen3-v1-held-out.md).

## Frozen gate result

| Metric | Threshold | Result | Outcome |
|---|---:|---:|:---:|
| Valid-schema rate | at least 95% | 100.0% | PASS |
| Escalation recall | at least 90% | 90.0% | PASS |
| Exact match | at least 70% | 60.0% | **FAIL** |
| `risk` slice escalation accuracy | 100% | 100.0% (n=2) | PASS |
| Median end-to-end latency | at most 60s | 36.83s | PASS |

The candidate missed one of five evaluated thresholds. Under the pre-committed
rule, that is a failed product decision even though four guardrails passed.

## Development-to-test change

| Metric | Development | Test | Delta |
|---|---:|---:|---:|
| Category accuracy | 97.5% | 85.0% | -12.5 pp |
| Priority accuracy | 77.5% | 65.0% | -12.5 pp |
| Escalation recall | 94.7% | 90.0% | -4.7 pp |
| Exact match | 72.5% | 60.0% | -12.5 pp |
| Valid schema | 100.0% | 100.0% | 0.0 pp |
| Median latency | 34.05s | 36.83s | +2.79s |

The development gate did not generalize to the frozen test gate. That is the
reason for separating prompt selection from final evaluation.

## Failure audit

Eight of 20 predictions were not exact matches:

- 7 wrong priorities;
- 3 wrong categories;
- 1 missed escalation;
- 1 unnecessary escalation;
- 3 examples with multiple errors.

The two multi-intent tickets both failed exact match. One combined blocked
access with a duplicate charge; the other combined an offline-mode request with
a crash. The prompt defines individual categories but not which intent wins,
making these failures partly a policy-specification problem.

The audit also exposed reference-policy tensions that must not be silently
fixed after the test:

- a desktop freeze with a working web workaround is labeled `high`, while the
  prompt describes meaningful friction with a workaround as `medium`;
- a personal-data export request is labeled `account_access`, but the category
  rules do not explicitly place privacy requests there;
- an unauthorized charge with legal language is labeled `urgent`, while the
  prompt places disputed money under `high` unless another urgent condition is
  explicit.

The recorded score stands. These observations inform the next dataset version;
they do not justify relabeling or rerunning this test.

## Reproduction

```bash
python3 run_eval.py \
  --models qwen3:4b \
  --split test \
  --prompt evals/support_triage/prompt.txt \
  --output-dir results/heldout-v1
```

- Dataset SHA-256:
  `d299f565faf9c7249e5164d75f16cd4f5be781235556fc108bbf7cbf3b5522c9`
- Prompt SHA-256:
  `9e1afd232a800aefb723984684d1b1aefc677a730feda13023c4d04b09f22f7b`
- Runtime and hardware: Ollama 0.32.1 on an Apple M1 Pro with 16 GB memory
- Sampling: temperature 0, one sequential run, no retries

Artifacts:

- [Generated gate report](comparison.md)
- [Raw machine-readable result](qwen3-4b-test.json)
- [Development model comparison](../2026-07-18-open-model-comparison/README.md)
- [Rejected prompt v2 experiment](../2026-07-18-priority-rubric-v2/README.md)

## What happens next

1. Treat the current test split as a public regression set, not a pristine
   held-out set.
2. Write explicit multi-intent, privacy-category, and priority-precedence rules.
3. Add new development examples for those policies without tuning on these
   eight test failures.
4. Collect a new test-set version before making another held-out claim.
5. Keep Qwen3 as a research baseline, not an adopted prototype.

Twenty synthetic examples cannot establish a stable population estimate or
production reliability. The value of this result is the disciplined rejection,
not the score itself.
