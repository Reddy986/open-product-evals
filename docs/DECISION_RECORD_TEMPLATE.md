# Evaluation decision record

Copy this file for each model, prompt, or product-policy decision. Fill it out
before running the held-out test split.

## Decision

What decision will this evaluation inform?

## Candidate and baseline

- Candidate model and exact revision:
- Current baseline:
- Inference runtime and version:
- Hardware:

## Product behavior

- Unit of evaluation:
- Intended use:
- Explicitly excluded uses:
- Most costly false positive:
- Most costly false negative:

## Data

- Dataset and version:
- Dataset fingerprint:
- Development example count:
- Test example count:
- Source and licensing:
- Known representation gaps:

## Metrics and pre-committed gate

| Metric | Threshold | Product rationale |
|---|---:|---|
| | | |

## Experiment

- Prompt fingerprint:
- Sampling settings:
- Repetitions:
- Command:
- Variables intentionally changed:

## Results

Link the machine-readable result and generated comparison report.

## Failure analysis

- Dominant error types:
- Weakest meaningful slices:
- Reference-label disagreements:
- Surprising qualitative examples:

## Recommendation

Choose one and explain why:

- adopt for the stated use;
- run a narrower or larger experiment;
- revise the prompt or policy;
- reject the candidate.

## Limitations and follow-up

State what the evidence does not establish, who should review the decision, and
what will trigger reevaluation.

