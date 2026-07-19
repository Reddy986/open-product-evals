# Calibrate a response-quality rubric before using an LLM judge

Model grading starts with a measurement question: can humans apply the proposed
rubric consistently? If not, optimizing a judge against one person's labels can
automate ambiguity rather than resolve it.

This v0.3 lab is deliberately dependency-free and human-first.

## 1. Read and freeze the policy

Both reviewers read:

- [the response-quality task](../evals/response_quality/TASK.md);
- [the draft rubric](../evals/response_quality/RUBRIC.md);
- the 12 public calibration examples, without any answer key.

Do not discuss individual examples before both reviews are complete.

## 2. Create separate annotation sheets

Reviewer A:

```bash
python3 calibrate_rubric.py init \
  --dataset evals/response_quality/dataset.jsonl \
  --reviewer reviewer-a \
  --output results/calibration-work/reviewer-a.jsonl
```

Reviewer B runs the same command with a different reviewer id and output file.
The command refuses to overwrite an existing file.

Each reviewer replaces every `null` with a 1–4 score or a boolean and may add a
short rationale in `notes`:

```json
{"id":"rq-cal-001","reviewer":"reviewer-a","dataset_fingerprint":"<generated SHA-256>","rubric_version":"v0.3-draft-1","scores":{"correctness":4,"policy_safety":4,"actionability":4,"communication":4},"critical_failure":false,"notes":"Claims remain appropriately qualified."}
```

The `results/calibration-work/` directory is ignored by Git to reduce accidental
leakage between reviewers. Keep the files private from the other reviewer until
both are frozen. Reviewer names should be stable pseudonyms if the files will be
published.

## 3. Measure agreement

```bash
python3 calibrate_rubric.py compare \
  results/calibration-work/reviewer-a.jsonl \
  results/calibration-work/reviewer-b.jsonl \
  --output results/calibration-work/calibration-report.md
```

The report includes:

- exact and within-one-point agreement for every dimension;
- matching dataset fingerprints and rubric versions;
- mean absolute score difference;
- quadratic weighted Cohen's kappa for the ordinal 1–4 scores;
- exact and positive agreement on critical failures;
- a ranked table of examples that require adjudication;
- the pre-committed pass/fail decision.

Kappa is not a truth score. Report it with score distributions, absolute
differences, example count, and concrete disagreements.

## 4. Adjudicate without laundering disagreement

Reviewers discuss every listed disagreement and cite the anchor or critical rule
that resolves it. Preserve the original review files. Record whether the result
was:

- one reviewer missed an explicit rule;
- an anchor was too vague;
- the ticket or response was genuinely ambiguous;
- the rubric lacked an important policy boundary.

If the rubric changes materially, its version changes too. Agreement measured on
the same examples is then diagnostic, not fresh evidence for the revised rubric.

## 5. Only then calibrate a model judge

Collect a separate, adjudicated set. Pre-commit the judge prompt, model revision,
temperature, dimensions, critical-failure gate, and retry policy. Compare the
judge with the human consensus and publish disagreement examples.

Do not claim that a judge is validated because it has a high correlation with
one reviewer, and do not hide critical failures inside an average score.

## Learning outcome

After this lab, you should be able to explain:

1. why subjective evals require a written rubric with observable anchors;
2. why human-human agreement comes before human-model agreement;
3. why ordinal agreement needs more than exact-match accuracy;
4. why critical failures need an independent gate;
5. why adjudication changes the measurement instrument and must be documented.
