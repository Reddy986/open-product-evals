# Evaluation comparison

| Candidate | Examples | Valid schema | Escalation recall | Exact match | Median latency | Gate |
|---|---:|---:|---:|---:|---:|:---:|
| gemma3:4b | 40 | 100.0% | 89.5% | 60.0% | 1.64s | FAIL |
| qwen3:4b | 40 | 100.0% | 94.7% | 72.5% | 34.05s | PASS |

## Gate definition

- `valid_schema_rate` ≥ 95.0%
- `escalation_recall` ≥ 90.0%
- `exact_match` ≥ 70.0%

This gate is a worked product hypothesis, not a production-safety certification. The public synthetic test set is too small to establish production reliability.

## Failure patterns

- **gemma3:4b**: wrong priority (16), multiple errors (7), wrong category (3)
- **qwen3:4b**: wrong priority (9), missed escalation (1), multiple errors (1)

## Gate misses

- **gemma3:4b** misses `escalation_recall`: 89.5% vs 90.0%.
- **gemma3:4b** misses `exact_match`: 60.0% vs 70.0%.

## Interpretation checklist

- Inspect individual failures before changing the prompt.
- Iterate on the development split; reserve the test split for comparison.
- Treat small score differences as inconclusive until repeated trials or uncertainty estimates are available.
- Revisit the gate when the product cost of false positives or false negatives changes.
