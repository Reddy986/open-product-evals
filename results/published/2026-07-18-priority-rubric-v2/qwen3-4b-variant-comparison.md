# Paired prompt-variant comparison

- **Model:** `qwen3:4b`
- **Split:** `development` (40 examples)
- **Dataset SHA-256:** `d299f565faf9c7249e5164d75f16cd4f5be781235556fc108bbf7cbf3b5522c9`
- **Temperature:** 0
- **Prompt v1 prompt SHA-256:** `9e1afd232a800aefb723984684d1b1aefc677a730feda13023c4d04b09f22f7b`
- **Prompt v2 prompt SHA-256:** `110d4bb03f679b3f9c3e80e61ce1680bd3864c903f36423b440c53801d00e3d9`

## Metric deltas

| Metric | Prompt v1 | Prompt v2 | Delta |
|---|---:|---:|---:|
| Category Accuracy | 97.5% | 95.0% | -2.5 pp |
| Priority Accuracy | 77.5% | 75.0% | -2.5 pp |
| Escalation Accuracy | 95.0% | 90.0% | -5.0 pp |
| Exact Match | 72.5% | 67.5% | -5.0 pp |
| Valid Schema Rate | 100.0% | 97.5% | -2.5 pp |
| Escalation Precision | 94.7% | 89.5% | -5.3 pp |
| Escalation Recall | 94.7% | 89.5% | -5.3 pp |

## Latency deltas

| Statistic | Prompt v1 | Prompt v2 | Delta |
|---|---:|---:|---:|
| Mean | 35.57s | 38.41s | +2.84s |
| Median | 34.05s | 34.66s | +0.61s |
| Max | 105.70s | 110.95s | +5.25s |

## Paired transitions

| Decision | Improved | Regressed | Net |
|---|---:|---:|---:|
| Exact match | 7 | 9 | -2 |
| Category | 1 | 2 | -1 |
| Priority | 6 | 7 | -1 |
| Escalation | 1 | 3 | -2 |

## Example transitions

- **Exact improvements:** `dev-005`, `dev-007`, `dev-012`, `dev-019`, `dev-022`, `dev-025`, `dev-040`
- **Exact regressions:** `dev-003`, `dev-013`, `dev-016`, `dev-017`, `dev-021`, `dev-030`, `dev-032`, `dev-034`, `dev-037`
- **Became invalid:** `dev-015`
- **Became valid:** none

> A paired development-set change shows regression behavior for these examples. It does not establish generalization, statistical significance, or production readiness.
