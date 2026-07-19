# Publishing trustworthy results

Result files contain raw predictions, normalized scores, error types, slice
metrics, latency summaries, and fingerprints for the dataset and prompt.

## Minimum reproducibility card

Every published model result should include:

- exact model tag or revision;
- inference runtime and version;
- operating system and hardware;
- command and dataset split;
- dataset and prompt SHA-256 fingerprints;
- sampling settings;
- date of the run;
- complete machine-readable result;
- known limitations and any failed product gates.

The runner records the evaluation fingerprints and temperature. Runtime and
hardware details remain manual because the local runner cannot identify them
reliably across platforms.

## Compare compatible runs

```bash
python3 compare_results.py results/model-a.json results/model-b.json \
  --output results/comparison.md
```

The comparison command rejects results with different dataset fingerprints,
splits, or example counts. You can change the worked-example thresholds:

```bash
python3 compare_results.py results/model-a.json results/model-b.json \
  --min-valid-schema 1.0 \
  --min-escalation-recall 0.95 \
  --min-exact-match 0.80
```

## Compare prompt variants on paired examples

When one model is run before and after a prompt change, use the paired command:

```bash
python3 compare_variants.py results/prompt-v1.json results/prompt-v2.json \
  --baseline-label "Prompt v1" \
  --candidate-label "Prompt v2" \
  --output results/prompt-change.md
```

The command requires the same model name, dataset fingerprint, split, selected
example count, temperature, record IDs, and expected labels. Prompt
fingerprints are expected to differ and are printed in the report. Every score
and latency statistic gets a baseline, candidate, and delta; paired transitions
show exact, category, priority, escalation, and schema-validity changes.

An invalid output receives no credit for an individual field, even if a value
could be recovered from the raw output. This keeps paired counts aligned with
the deterministic scorer. Development-set changes reveal regression behavior
on those examples; they do not establish generalization.

## Claims to avoid

- “Model A is better” from one small synthetic test.
- “Production ready” because an illustrative gate passed.
- “Deterministic” merely because temperature is zero.
- “Unbiased” because the examples are public and inspectable.
- “Statistically significant” without a justified uncertainty analysis.

Prefer a bounded claim:

> On version X of this synthetic test set, using the recorded prompt and local
> runtime, Model A missed fewer escalation cases than Model B. More representative
> data and repeated trials are needed before a production decision.

## After a held-out test is used

A test split is not pristine after its predictions and failures influence the
next prompt, policy, labels, or model choice. Keep the result, publish failed
gates, and mark the split as consumed. Future runs may use it as a regression
suite, but should disclose the prior exposure.

To make another held-out claim after learning from test failures, version the
dataset and collect a new test split. Do not relabel failures, rerun individual
examples, or move the threshold after seeing the score.

For this repository, use the contributor-executable
[dataset v2 held-out protocol](../evals/support_triage/DATASET_V2_PROTOCOL.md).
It keeps new test content sealed from prompt authors, requires independent
labels and adjudication, and publishes the complete result whether it passes or
fails.
