# Worked example: rejecting the keyword baseline

This report demonstrates how to turn evaluation output into a bounded product
recommendation. The candidate is a transparent keyword classifier, **not an
LLM**. It is included to test the evaluation workflow and provide an intentionally
imperfect result for error analysis.

## Decision

Should the keyword baseline automatically triage support tickets under the
worked gate in `TASK.md`?

**Recommendation: reject it as an automation candidate.** Keep it only as a
pipeline sanity check.

## Run

```bash
python3 run_baseline.py --split development \
  --output results/baseline-development.json
python3 compare_results.py results/baseline-development.json
```

These values come from the 40-example development split. They are reproducible
from the repository, but they are not evidence of generalization.

| Candidate | Examples | Valid schema | Escalation recall | Exact match | Gate |
|---|---:|---:|---:|---:|:---:|
| keyword-baseline-v1 (not an LLM) | 40 | 100.0% | 63.2% | 50.0% | FAIL |

The worked gate requires:

- valid-schema rate ≥ 95%;
- escalation recall ≥ 90%;
- exact match ≥ 70%.

## Why the average is misleading

Category accuracy is 87.5%, which may initially look promising. The baseline
still misses 7 of the 19 development examples that require human escalation.
That failure mode matters more than average routing accuracy because the missed
set includes cases that may need time-sensitive investigation or action.

Dominant errors:

| Error type | Count |
|---|---:|
| Wrong priority | 16 |
| Missed escalation | 7 |
| Wrong category | 5 |
| Examples with multiple errors | 8 |

## What to do next

1. Inspect every missed escalation and check the reference labels.
2. Turn recurring failures into policy clarifications or behavioral slices.
3. Run an open model on the same development examples.
4. Compare identical dataset fingerprints and example counts.
5. Use the test split only after selecting the prompt and product gate.

## Limitations

- The rules and public labels are fully visible, so this is not a benchmark of
  unseen generalization.
- The synthetic development split is small and not representative traffic.
- Slice results with one example identify hypotheses, not stable estimates.
- Passing the illustrative gate would not establish production readiness.

