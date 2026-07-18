# Changelog

## 0.2.1 — First open-model comparison

- Publish reproducible Qwen3 4B and Gemma 3 4B development runs with raw outputs.
- Document the quality-versus-latency decision, failure review, and limitations.
- Record runtime, hardware, model IDs, quantization, and artifact fingerprints.
- Keep in-repository result paths portable across contributor machines.
- Make the documented smoke test use the development split.

## 0.2.0 — Error analysis and learning workflow

- Add a zero-setup transparent keyword baseline.
- Report per-slice category, priority, escalation, schema, and exact-match metrics.
- Classify dominant failure types, including missed and unnecessary escalations.
- Record prompt and dataset fingerprints in model results.
- Compare compatible runs with explicit, configurable product gates.
- Add a hands-on eval curriculum and trustworthy-results guide.
- Add automated tests and structured contribution templates.

## 0.1.0 — Support triage

- Publish 60 synthetic, manually reviewed support tickets.
- Define an inspectable category, priority, and escalation policy.
- Add deterministic scoring and a standard-library Ollama runner.
- Separate development and held-out test examples.
