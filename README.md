# Open Product Evals

**Small, transparent evaluations for real LLM product decisions.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-2ea44f.svg)](LICENSE)
[![Status: v0.2](https://img.shields.io/badge/status-v0.2-blue.svg)](#roadmap)

Open Product Evals is a learning-in-public project: each evaluation starts with a concrete product question, an inspectable dataset, deterministic scoring, and an honest account of what the results do—and do not—prove.

The first question is deliberately narrow:

> **Can a small local model reliably triage customer-support tickets?**

## See the task

Input:

```text
Someone changed my password and I cannot access my account.
```

Expected output:

```json
{
  "category": "account_access",
  "priority": "urgent",
  "escalate": true
}
```

The runner asks each local model to classify 20 held-out synthetic tickets, then reports category accuracy, priority accuracy, escalation precision and recall, exact match, schema validity, latency, and performance on behavioral slices.

## Why this exists

Generic leaderboards do not answer a product question such as “is this model reliable enough for our workflow?” This repository explores how to turn product requirements into reproducible acceptance tests.

The project favors clarity over breadth:

- one product task;
- 60 manually reviewed synthetic examples;
- a published labeling policy;
- deterministic, dependency-free scoring;
- local inference through Ollama;
- no customer, employer, or proprietary data.

## Try the complete eval loop in 60 seconds

No model or package installation is required for the transparent sanity-check
baseline:

```bash
python3 run_baseline.py --split development --output results/baseline.json
python3 compare_results.py results/baseline.json
```

The baseline is deliberately simple and is **not an LLM**. It exists so a new
contributor can immediately inspect scoring, behavioral slices, error taxonomy,
and a product decision gate.

Follow the hands-on [Learn LLM evals by doing](docs/EVALS_101.md) path to turn
this example into a disciplined model experiment.

See the [worked baseline decision](examples/keyword-baseline-development.md) for
an example of rejecting a candidate despite apparently strong category accuracy.

## Run open models locally

### 1. Install and start Ollama

Follow the instructions at [ollama.com](https://ollama.com/), then pull two small models:

```bash
ollama pull qwen3:4b
ollama pull gemma3:4b
```

### 2. Run a smoke test

```bash
python3 run_eval.py --models qwen3:4b gemma3:4b --limit 3
```

### 3. Run the held-out test split

```bash
python3 run_eval.py --models qwen3:4b gemma3:4b --split test
```

Machine-readable results are written to `results/` and excluded from Git by default so you can decide what to publish.

### 4. Compare compatible results

```bash
python3 compare_results.py results/model-a.json results/model-b.json \
  --output results/comparison.md
```

The comparison checks dataset fingerprints, summarizes dominant failure modes,
and applies an explicit risk-first product gate. Read
[Publishing trustworthy results](docs/RESULTS_GUIDE.md) before sharing scores.
Use the [decision-record template](docs/DECISION_RECORD_TEMPLATE.md) to commit to
the product question, thresholds, and next actions before looking at test data.

No Python packages are required; the runner uses only the standard library.

## What gets measured

| Metric | Product meaning |
|---|---|
| Category accuracy | Did the ticket reach the right queue? |
| Priority accuracy | Was urgency classified correctly? |
| Escalation recall | How many cases needing a human were caught? |
| Escalation precision | How many escalations were actually necessary? |
| Exact match | Were all three decisions correct? |
| Valid-schema rate | Could downstream software parse the answer? |
| Slice accuracy | Where does the model fail: ambiguity, privacy, outages, multi-intent tickets, and more? |
| Error taxonomy | Is the failure structural, routing-related, priority-related, or an escalation miss? |

The most important initial metric is **escalation recall**. A high average score is not useful if the model silently misses compromised accounts or disputed charges.

Read the full [task and labeling specification](evals/support_triage/TASK.md).

## Dataset

`evals/support_triage/dataset.jsonl` contains:

- 40 development examples for prompt iteration and error analysis;
- 20 test examples for comparison;
- explicit expected labels;
- behavioral slices such as `compromise`, `privacy`, `multi_intent`, `ambiguous`, and `human_action`.

All examples are fictional and manually reviewed. Public labels make this a useful educational and regression suite, not a contamination-resistant benchmark.

## Validate the repository

```bash
python3 -m unittest discover -v
python3 -m compileall -q open_product_evals run_eval.py run_baseline.py compare_results.py
```

## What v0.2 adds

- zero-setup transparent baseline;
- category, priority, escalation, schema, and exact-match metrics for every slice;
- explicit failure types and dominant-error summaries;
- dataset and prompt fingerprints for comparable runs;
- Markdown comparison reports with configurable product gates;
- a practical eval-learning curriculum;
- automated tests across supported Python versions;
- a structured edge-case contribution form.

## Roadmap

- **v0.1 — Triage:** objective labels, deterministic graders, local open-model runner
- **v0.2 — Error analysis:** richer slice reports, reproducibility fingerprints, comparison gates
- **v0.3 — Response quality:** rubric design and human-calibrated model grading
- **v0.4 — Model selection:** repeated trials, confidence intervals, memory and throughput
- **v0.5 — New workflow:** customer-feedback extraction or RAG answer verification

The long-term goal is not another generic evaluation framework. It is a growing set of practical, inspectable evaluations that connect model behavior to product decisions.

## Contributing

The easiest contributions are realistic edge cases, label-policy critiques, scoring tests, and adapters for additional local runtimes. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Independence

This is an independent personal project. It is not affiliated with or endorsed by any employer or model provider.

## License

[MIT](LICENSE). Model weights are not included; evaluate the terms of any model you choose to run.
