# Changelog

## 0.2.3 — Paired prompt-regression reports

- Add a standard-library command for comparing one model across two prompts.
- Reject comparisons that change model, data, split, count, or temperature.
- Report metric, latency, exact-match, field-level, and schema transitions.
- Publish generated reports for the rejected priority-rubric experiment.
- Correct one hand-counted Qwen escalation transition exposed by the report.

## 0.2.2 — Frozen test decision

- Publish a pre-committed priority-rubric experiment and its rejection.
- Publish the first one-time Qwen3 held-out run and failed product decision.
- Mark the consumed test split as a public regression set.
- Default the model runner to the development split.
- Document multi-intent and reference-policy gaps without changing test scores.

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
