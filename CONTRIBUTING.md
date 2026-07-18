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

## Development

Run the checks before opening a pull request:

```bash
python3 -m unittest discover -v
python3 -m compileall -q open_product_evals run_eval.py run_baseline.py compare_results.py
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
