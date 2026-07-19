# Contributing

Thanks for helping make product-focused LLM evaluations more useful and trustworthy.

## Good first contributions

- Propose a difficult but realistic support ticket.
- Identify a disagreement with the current labeling policy.
- Add a scoring or dataset-validation test.
- Improve documentation for first-time evaluation practitioners.
- Reproduce a benchmark and report your hardware and software versions.

## Adding a dataset example

Every example must:

1. Be fictional or safely licensed for redistribution.
2. Include an expected `category`, `priority`, and `escalate` value.
3. Include at least one behavioral slice.
4. Follow the definitions in `evals/support_triage/TASK.md`.
5. Avoid real names, emails, account numbers, secrets, or customer data.

If the correct label is debatable, open an issue before submitting the example. Label disagreement is useful evaluation information, not something to hide.

The current test split is consumed. Do not add a few examples to it and call it
held out. Any new held-out collection must follow the design-first
[dataset v2 protocol](evals/support_triage/DATASET_V2_PROTOCOL.md). The protocol
requires a frozen policy, original fictional sourcing, two independent
reviewers, adjudication, access separation, artifact fingerprints, and a
one-time public release rule.

## Challenge the v0.3 response-quality rubric

A useful non-code contribution is an independent score for one public
response-quality example:

1. Read `evals/response_quality/TASK.md` and `RUBRIC.md`.
2. Choose one record from `evals/response_quality/dataset.jsonl`.
3. Score all four dimensions and the independent critical-failure flag before
   looking for anyone else's score.
4. Open a **Challenge a response-quality score** issue and cite the exact anchor
   or rule behind the judgment.

Disagreement is not treated as reviewer error by default. It may reveal a vague
anchor, a missing policy boundary, or an ambiguous example. Full calibration
files should follow `docs/RUBRIC_CALIBRATION.md` so dataset fingerprints, rubric
versions, and blind-review discipline remain inspectable.

## Development

Run the checks before opening a pull request:

```bash
python3 -m unittest discover -v
python3 -m compileall -q open_product_evals run_eval.py run_baseline.py compare_results.py compare_variants.py calibrate_rubric.py
```

The project currently requires Python 3.10 or newer and intentionally has no third-party Python dependencies.

## Benchmark results

When sharing results, include:

- exact model tag or revision;
- Ollama version;
- operating system and hardware;
- dataset split;
- command used;
- raw machine-readable result when practical.

Do not present a small difference as meaningful without repeated trials or uncertainty estimates.

Use the [results guide](docs/RESULTS_GUIDE.md) and include the generated comparison
report when proposing a model or prompt change.
