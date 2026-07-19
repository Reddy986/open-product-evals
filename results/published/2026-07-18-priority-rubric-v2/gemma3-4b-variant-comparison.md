# Paired prompt-variant comparison

- **Model:** `gemma3:4b`
- **Split:** `development` (40 examples)
- **Dataset SHA-256:** `d299f565faf9c7249e5164d75f16cd4f5be781235556fc108bbf7cbf3b5522c9`
- **Temperature:** 0
- **Prompt v1 prompt SHA-256:** `9e1afd232a800aefb723984684d1b1aefc677a730feda13023c4d04b09f22f7b`
- **Prompt v2 prompt SHA-256:** `110d4bb03f679b3f9c3e80e61ce1680bd3864c903f36423b440c53801d00e3d9`

## Metric deltas

| Metric | Prompt v1 | Prompt v2 | Delta |
|---|---:|---:|---:|
| Category Accuracy | 92.5% | 90.0% | -2.5 pp |
| Priority Accuracy | 60.0% | 50.0% | -10.0 pp |
| Escalation Accuracy | 90.0% | 77.5% | -12.5 pp |
| Exact Match | 60.0% | 40.0% | -20.0 pp |
| Valid Schema Rate | 100.0% | 100.0% | +0.0 pp |
| Escalation Precision | 89.5% | 100.0% | +10.5 pp |
| Escalation Recall | 89.5% | 52.6% | -36.8 pp |

## Latency deltas

| Statistic | Prompt v1 | Prompt v2 | Delta |
|---|---:|---:|---:|
| Mean | 1.66s | 2.06s | +0.40s |
| Median | 1.64s | 1.88s | +0.24s |
| Max | 2.00s | 8.46s | +6.45s |

## Paired transitions

| Decision | Improved | Regressed | Net |
|---|---:|---:|---:|
| Exact match | 2 | 10 | -8 |
| Category | 0 | 1 | -1 |
| Priority | 3 | 7 | -4 |
| Escalation | 2 | 7 | -5 |

## Example transitions

- **Exact improvements:** `dev-034`, `dev-036`
- **Exact regressions:** `dev-004`, `dev-005`, `dev-008`, `dev-011`, `dev-021`, `dev-022`, `dev-025`, `dev-026`, `dev-032`, `dev-033`
- **Became invalid:** none
- **Became valid:** none

> A paired development-set change shows regression behavior for these examples. It does not establish generalization, statistical significance, or production readiness.
