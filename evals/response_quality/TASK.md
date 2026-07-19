# Response quality calibration task

Status: `v0.3-draft`

## Product question

> Can reviewers apply one response-quality rubric consistently enough to use it
> as the reference for a future model judge?

This is deliberately a **human-human calibration task first**. It does not ask
whether an LLM judge agrees with one person, and it does not make a production
claim about any support system.

## Unit of review

Each public calibration record contains:

- a fictional customer-support ticket;
- a fictional draft response;
- behavioral slices for analysis;
- no gold score and no hidden answer.

Review the ticket and response together. Score the response that is present; do
not silently rewrite it into a better response.

## Outputs

Assign four integer scores from 1 to 4 using [RUBRIC.md](RUBRIC.md):

- `correctness`;
- `policy_safety`;
- `actionability`;
- `communication`.

Also assign `critical_failure` as `true` or `false`. This flag is independent of
the four scores: do not infer it from an average.

## Blind calibration protocol

1. Freeze this task, the rubric, the dataset, and the agreement thresholds.
2. Generate one annotation sheet per reviewer with `calibrate_rubric.py init`.
3. Reviewers score every example independently and do not inspect each other's
   files, notes, or summary statistics.
4. Generate an agreement report with `calibrate_rubric.py compare`.
5. Adjudicate every disagreement by citing a rubric rule.
6. If adjudication changes the rubric materially, repeat calibration on fresh
   examples. Do not reuse agreement on the same examples as evidence that the
   revised rubric generalizes.

## Pre-committed smoke-calibration gates

Before comparing reviewers, this draft commits to:

- quadratic weighted Cohen's kappa of at least `0.60` for every dimension;
- mean absolute score difference of at most `0.50` for every dimension;
- critical-failure exact agreement of at least `90%`;
- at least two positive and two negative critical-failure labels from each
  reviewer, so a constant label cannot pass by accident.

These gates only determine whether the rubric is understandable enough for the
next iteration. Twelve public examples are too few to validate a model judge.

## Future judge-calibration rule

Do not tune and evaluate a judge on these same records. A later judge experiment
must use a separately collected, human-adjudicated development set and a frozen
evaluation set. It must report agreement by dimension, critical-failure recall,
score distributions, and disagreements—not only one correlation coefficient.

## Data and independence

All tickets and responses are original, fictional examples. They contain no
customer, employer, or proprietary data. This task is independent personal work
and is not affiliated with or endorsed by any employer or model provider.
