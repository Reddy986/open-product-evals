# Evaluation comparison

| Candidate | Examples | Valid schema | Escalation recall | Exact match | Median latency | Gate |
|---|---:|---:|---:|---:|---:|:---:|
| gemma3:4b | 40 | 100.0% | 52.6% | 40.0% | 1.88s | FAIL |
| qwen3:4b | 40 | 97.5% | 89.5% | 67.5% | 34.66s | FAIL |

## Gate definition

- `valid_schema_rate` ≥ 95.0%
- `escalation_recall` ≥ 90.0%
- `exact_match` ≥ 70.0%

This gate is a worked product hypothesis, not a production-safety certification. The public synthetic test set is too small to establish production reliability.

## Failure patterns

- **gemma3:4b**: wrong priority (20), missed escalation (9), multiple errors (9)
- **qwen3:4b**: wrong priority (9), missed escalation (2), multiple errors (2)

## Gate misses

- **gemma3:4b** misses `escalation_recall`: 52.6% vs 90.0%.
- **gemma3:4b** misses `exact_match`: 40.0% vs 70.0%.
- **qwen3:4b** misses `escalation_recall`: 89.5% vs 90.0%.
- **qwen3:4b** misses `exact_match`: 67.5% vs 70.0%.

## Interpretation checklist

- Inspect individual failures before changing the prompt.
- Iterate on the development split; reserve the test split for comparison.
- Treat small score differences as inconclusive until repeated trials or uncertainty estimates are available.
- Revisit the gate when the product cost of false positives or false negatives changes.
