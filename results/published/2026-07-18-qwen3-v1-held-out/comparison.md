# Evaluation comparison

| Candidate | Examples | Valid schema | Escalation recall | Exact match | Median latency | Gate |
|---|---:|---:|---:|---:|---:|:---:|
| qwen3:4b | 20 | 100.0% | 90.0% | 60.0% | 36.83s | FAIL |

## Gate definition

- `valid_schema_rate` ≥ 95.0%
- `escalation_recall` ≥ 90.0%
- `exact_match` ≥ 70.0%

This gate is a worked product hypothesis, not a production-safety certification. The public synthetic test set is too small to establish production reliability.

## Failure patterns

- **qwen3:4b**: wrong priority (7), multiple errors (3), wrong category (3)

## Gate misses

- **qwen3:4b** misses `exact_match`: 60.0% vs 70.0%.

## Interpretation checklist

- Inspect individual failures before changing the prompt.
- Iterate on the development split; reserve the test split for comparison.
- Treat small score differences as inconclusive until repeated trials or uncertainty estimates are available.
- Revisit the gate when the product cost of false positives or false negatives changes.
