# Learn LLM evals by doing

This repository is a small laboratory for learning the reasoning behind good
evaluations. The code matters, but the core skill is turning an ambiguous
product concern into evidence that supports a decision.

## The evaluation loop

1. **Name the decision.** What will change if the evaluation passes or fails?
2. **Define observable behavior.** What input and output can be inspected?
3. **Write the labeling policy.** A second person should be able to reproduce a label.
4. **Build development cases.** Include ordinary cases, boundaries, and costly failures.
5. **Choose decision-linked metrics.** Average accuracy is rarely enough.
6. **Set a gate before seeing test results.** Encode the product's tolerance for failure.
7. **Iterate on development data.** Inspect failures; do not merely chase a score.
8. **Use the test split sparingly.** Report limitations and avoid overclaiming.

For support triage, the costly behavior is silently failing to escalate a risky
ticket. That is why escalation recall is a gate, while latency is initially a
diagnostic rather than the primary optimization target.

## Lab 0: prove the harness works

Run the transparent keyword baseline. It is not an LLM and is not meant to be
competitive; it lets you exercise the full measurement loop with no setup.

```bash
python3 run_baseline.py --split development --output results/baseline-development.json
```

Answer these questions before changing anything:

- Which three error types occur most often?
- Which slices have the lowest exact-match rate?
- Does a weak slice contain enough examples to support a conclusion?
- Which errors would be most expensive in a real workflow?

## Lab 1: audit labels, not models

Read ten development examples and label them without looking at `expected`.
Compare your answers with the file and note disagreements.

A disagreement can mean:

- you overlooked the labeling policy;
- the policy is underspecified;
- the example is ambiguous;
- the published label is wrong.

Do not resolve every disagreement by making the policy longer. If reasonable
reviewers still disagree, measure agreement and consider representing ambiguity
instead of forcing a false gold label.

## Lab 2: run one open model

After starting Ollama and pulling a model:

```bash
python3 run_eval.py --models qwen3:4b --split development --limit 10
```

Inspect raw outputs and classify each failure. Separate failures caused by:

- invalid output structure;
- taxonomy confusion;
- priority-policy confusion;
- missed escalation;
- unnecessary escalation;
- an ambiguous or questionable reference label.

The scorer records these categories automatically, but reading examples is what
turns counts into product understanding.

## Lab 3: run a controlled prompt experiment

Copy `evals/support_triage/prompt.txt`, make one purposeful change, and run both
prompts on the same development examples. Write down your hypothesis first.

Good hypothesis:

> Adding two boundary examples will improve priority accuracy on workaround
> cases without reducing escalation recall.

Weak hypothesis:

> This prompt is better.

Change one variable at a time. Keep both result files, then compare them:

```bash
python3 compare_results.py results/run-a.json results/run-b.json
```

## Lab 4: compare models against a product gate

Run at least two model tags on the complete development split. Compare the exact
same dataset fingerprint and example count.

```bash
python3 run_eval.py --models qwen3:4b gemma3:4b --split development
python3 compare_results.py results/qwen-result.json results/gemma-result.json \
  --output results/comparison.md
```

The default worked-example gate requires:

- valid-schema rate of at least 95%;
- escalation recall of at least 90%;
- exact-match accuracy of at least 70%.

These thresholds are hypotheses, not universal standards. Explain how product
costs justify any threshold you publish.

## Lab 5: freeze a decision record

Before using the test split, write a short decision record:

```text
Decision:
Candidate models:
Dataset fingerprint:
Primary risk:
Metrics and thresholds chosen in advance:
Expected product action if the gate passes:
Expected product action if the gate fails:
Known limitations:
```

Then run the held-out split once. If you change the prompt or policy in response,
the test set has become development data; version the evaluation and create a
new test set before making a fresh generalization claim.

## How to know you are improving at evals

You are progressing when you can:

- explain why each metric maps to a product cost;
- find label problems before blaming the model;
- distinguish regression tests from claims about generalization;
- design behavioral slices before looking at model failures;
- resist ranking models when the sample is too small;
- make a clear ship, experiment, or reject recommendation with caveats.

The goal is not a perfect score. It is a decision process that another person
can inspect, reproduce, challenge, and improve.

