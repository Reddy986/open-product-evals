# Dataset v2 held-out protocol

- **Protocol version:** 1.0
- **Status:** design frozen by merge; no v2 held-out examples have been collected or labeled
- **Scope:** support-ticket triage dataset v2

This document must be approved before anyone collects held-out tickets for
dataset v2. It separates policy design, data collection, prompt development,
and final evaluation so a future held-out result can support a bounded product
decision.

The existing 20-example test split remains permanently consumed. It may be
used for regression testing, but it must never be described as unseen again.

## 1. Product claim

Dataset v2 will test this claim:

> A frozen open-weight model and prompt can propose category, priority, and
> escalation labels for one English-language SaaS support message with enough
> reliability and latency for an offline shadow-mode prototype in which a human
> reviews every prediction before any action is taken.

Passing the v2 gate may justify only that human-reviewed offline prototype. It
will not justify autonomous routing, customer-facing responses, production
deployment, safety-critical use, multilingual performance, or a claim about all
real support traffic.

### Target scenario distribution

The target is a deliberately risk-weighted synthetic distribution, not an
estimate of a particular company's traffic:

- one fictional inbound support message with no private conversation history;
- English-language SaaS account, billing, feature, technical, and policy cases;
- a mix of ordinary self-service requests and costly human-action cases;
- explicit stress coverage for the failure modes in section 4;
- no real customer, employer, account, or production data.

The published result must call this a **risk-weighted synthetic test**. It must
not call the scores production prevalence estimates.

## 2. Two different data uses

| Artifact | Who may inspect it before the final run? | Permitted use |
|---|---|---|
| v1 development split | Everyone | Learning, prompt iteration, and regression |
| v1 consumed test split | Everyone | Regression only; never a new held-out claim |
| v2 development split | Everyone after its separate public release | Policy examples, prompt iteration, and candidate selection |
| v2 sealed held-out split | Custodian and labeling team only | One pre-committed final decision |

The v2 held-out tickets, labels, and per-example slice assignments remain
outside the public repository until the one-time run is finished. Prompt
authors may see the policy, aggregate quotas, v2 development data, and v1
regression data. They may not see v2 held-out ticket text, labels, rationales,
or model outputs before the result is sealed.

After the result is published, the v2 held-out split becomes another public
regression set. It does not regain held-out status later.

## 3. Minimum size and balance

Dataset v2 must contain at least:

- **100 new public development examples**; and
- **100 new sealed held-out examples**.

The minimum of 100 held-out examples is four times the size of the consumed
test. Each example changes an overall accuracy by one percentage point. With at
least 40 escalation-positive tickets, one missed escalation changes recall by
at most 2.5 percentage points. Required slices have at least 10 examples, so a
slice result is not determined by a single anecdote.

This is a coverage and decision-granularity rationale, not a statistical-power
claim. One hundred synthetic examples are still too few to prove a 90% or 95%
population rate with a tight confidence interval. The release must publish
Wilson 95% intervals for binomial metrics and retain the production-reliability
limitation even if every gate passes.

The quotas also address concrete v1 gaps. Its consumed test has only two
multi-intent, two privacy, two workaround, one adversarial-tone, and one
ambiguous example. Its development split has no `general_question` examples.
Those tiny denominators are useful failure prompts, not stable slice evidence.
V2 raises coverage without copying any of those ticket scenarios.

### Held-out marginal balance

All rules below apply to the final 100-or-more held-out examples:

| Dimension | Required balance |
|---|---|
| Category | At least 15 examples in each of the five categories; no category above 30% |
| Priority | At least 15 examples at each of `low`, `medium`, `high`, and `urgent`; no priority above 35% |
| Escalation | 40%–60% `true` and 40%–60% `false` |
| Ordinary controls | At least 25 low-risk, single-intent cases that should not be escalated |
| Critical human action | At least 30 compromise, fraud, privacy, outage, or confirmed missing-data cases requiring a human |

Counts may exceed 100 if the collection team needs more examples to satisfy
all margins without forcing unnatural tickets. No ticket may be duplicated to
fill more than one row; behavioral slices may overlap naturally.

## 4. Required held-out coverage

The scenario planner records aggregate counts before prose is written. The
held-out split must meet every minimum below:

| Slice | Minimum | Composition rule |
|---|---:|---|
| `multi_intent` | 15 | At least six distinct intent pairings; no pairing appears more than four times |
| `privacy` | 10 | Include access, export, deletion, consent, and disclosure concerns |
| `fraud` | 15 | Include unrecognized charges, payment abuse, and identity/account misuse |
| `outage` | 10 | Mix systemic outages with isolated degradation; do not equate every failure with an outage |
| `missing_data` | 10 | Mix confirmed loss with delayed sync, hidden state, and incomplete evidence |
| `workaround` | 15 | Include both acceptable workarounds and stopped-work cases where a workaround is inadequate |
| `adversarial_tone` | 10 | At least four should remain non-urgent and non-escalated so tone alone cannot determine labels |
| `ambiguous_priority` | 15 | Omit or conflict on facts needed for priority; apply a frozen fallback rule |
| `critical_human_action` | 30 | Compromise, fraud, privacy, outage, or confirmed missing-data cases labeled for human action |
| `ordinary_control` | 25 | Low-risk single-intent cases that should remain self-service and non-escalated |

Additional requirements:

- At least 20 tickets belong to two or more required slices.
- Every required slice includes at least two categories and two priorities.
- Multi-intent examples include both compatible and conflicting label outcomes.
- At least 10 tickets are deliberately close to a policy boundary without
  copying the wording or factual structure of a v1 failure.
- Aggregate coverage is public; individual held-out assignments remain sealed.

## 5. Policy freeze before final labels

Create `TASK_V2.md` and freeze it before either reviewer finalizes a held-out
label. It must resolve all of the following:

1. Category precedence for multi-intent tickets.
2. The category for privacy access, export, deletion, and disclosure requests.
3. Priority precedence for compromise, fraud, legal threats, outages, missing
   data, blocked work, deadlines, and available workarounds.
4. Whether uncertainty or missing context lowers priority, triggers escalation,
   or uses a dedicated deterministic fallback.
5. The exact distinction between priority and escalation.
6. Treatment of abusive or adversarial tone independent of the underlying risk.
7. Category, priority, and escalation rules for out-of-scope requests.
8. The output schema, accepted normalization, grader behavior, and slice
   definitions.

The frozen policy receives a version and SHA-256 fingerprint. If adjudication
reveals a policy gap, stop labeling, revise and re-fingerprint the policy, and
have both reviewers re-review every affected example independently. Do not
patch only the example that exposed the gap.

The prompt may be written after the policy is frozen. Held-out labels must be
derived from the policy, never from what a candidate model predicts.

## 6. Source tickets without copying v1 failures

All tickets must be original fictional text written for this project and
redistributable under the repository's MIT license. Do not copy or paraphrase
real support tickets, benchmark examples, the consumed v1 test cases, or their
published model failures.

Use this process:

1. A scenario planner creates abstract cards containing only dimensions such as
   category family, risk type, context availability, workaround state, intent
   count, and tone. Cards contain no ticket prose and no final labels.
2. The custodian assigns cards to at least two writers who declare whether they
   have previously studied the v1 consumed test.
3. A writer who remembers a v1 test item must not author the corresponding
   scenario family. Exposure is disclosed; it is not hidden.
4. Writers produce tickets without opening the v1 test or its failure reports
   during drafting. They may use `TASK_V2.md`.
5. The custodian checks the drafts against every v1 ticket for exact,
   normalized, and high lexical similarity. Automated similarity is a review
   flag, not proof that a semantic paraphrase is safe.
6. A reviewer compares every flagged pair and either documents why the new
   scenario is substantively different or replaces it before labeling.

Learning an abstract policy gap from v1 is allowed. Rewriting “blocked access
plus duplicate charge” with synonyms is not. New examples must vary the
underlying situation, decision boundary, and relevant evidence—not merely the
surface wording.

## 7. Roles and access separation

Record GitHub handles or stable contributor IDs for these roles:

| Role | Responsibility | Must not do |
|---|---|---|
| Protocol owner | Maintains this process and public checklist | View sealed examples while authoring the candidate prompt |
| Scenario planner | Creates the aggregate coverage matrix | Write final ticket prose or labels for the same cards |
| Ticket writers | Create original fictional messages | Tune or choose the candidate prompt/model |
| Reviewer A | Labels independently against frozen policy | See Reviewer B's labels before submission |
| Reviewer B | Labels independently against frozen policy | See Reviewer A's labels before submission |
| Adjudicator | Resolves disagreements using policy citations | Replace the frozen policy silently |
| Data custodian | Controls sealed artifacts, hashes, and final execution | Share held-out content with prompt authors before publication |
| Prompt/model owner | Uses only development and regression data | Access held-out text, labels, rationales, or outputs |

One person may hold compatible roles, but:

- no one reviews a ticket they wrote;
- Reviewer A, Reviewer B, and the adjudicator are different people for a given
  example;
- the prompt/model owner cannot be a held-out writer, reviewer, adjudicator, or
  custodian;
- everyone with held-out access signs an exposure declaration before receiving
  access.

If the project cannot staff this separation, it may still publish a new public
regression batch, but it must not call the result held out.

## 8. Independent labeling and adjudication

Reviewer A and Reviewer B label each ticket independently. Neither reviewer
sees model output or the other reviewer's work. Each review records:

- `category`, `priority`, and `escalate`;
- behavioral slices;
- a short rationale citing `TASK_V2.md` sections;
- confidence: `clear`, `boundary`, or `policy_gap`.

Before adjudication, publish or preserve an aggregate agreement report with:

- raw agreement and Cohen's kappa for category, priority, and escalation;
- per-slice disagreement counts;
- the fraction of examples requiring adjudication;
- no ticket text, labels, or rationales.

Proceed only if each primary field has kappa of at least 0.80 and no more than
15% of examples require adjudication. Missing either threshold triggers a policy
or collection review and a new independent labeling round for affected batches.

The adjudicator resolves every remaining disagreement by citing the frozen
policy. The disagreement log records only example ID, disputed fields, policy
section, resolution type, and whether a policy revision was required. All
examples require a final resolved label; unresolved examples are removed and
replaced before sealing, never dropped after model scoring.

## 9. Seal and pre-commitment

The data custodian canonicalizes UTF-8 JSONL with one object per line and a
terminal newline. Use semantic versions for released data: `2.0.0` is the first
revealed v2 artifact. Corrections after release increment the patch version and
retain a changelog, but the score remains attached to the exact artifact used.
A future unseen claim requires a new major held-out collection, not a patched
copy of a consumed split.

Before the run, every content, label, policy, or canonicalization change
invalidates the current seal. Increment the release-candidate identifier,
repeat affected reviews, and publish new hashes before selecting a candidate.

The release manifest records:

- dataset semantic version;
- protocol version and SHA-256;
- policy version and SHA-256;
- development content SHA-256;
- sealed held-out ticket-text SHA-256;
- sealed held-out label SHA-256;
- complete labeled held-out artifact SHA-256;
- count and aggregate coverage table for each split;
- source and license declaration;
- reviewer, adjudicator, and exposure declarations;
- collection, label-freeze, seal, and run timestamps.

Store the sealed held-out artifact in access-controlled storage with an audit
log and a second encrypted backup. Do not commit it to a branch, pull request,
GitHub Actions artifact, issue, or public release before the final run.

The public seal commit contains the hashes, counts, coverage aggregates, and
declarations—but no held-out ticket text or labels. Any byte change after that
commit invalidates the seal and requires a new version and review cycle.

## 10. Candidate selection and frozen gate

The prompt/model owner may iterate on v2 development data and both public v1
splits. Before the one-time held-out run, a public decision record must freeze:

- the product claim and excluded uses;
- one candidate model, exact weight/revision ID, quantization, and license;
- prompt text and SHA-256;
- runner, parser, scorer, and policy fingerprints;
- runtime, hardware, sampling, retry, and concurrency settings;
- the full command and output-handling procedure;
- every threshold and the rule that all thresholds must pass;
- what happens after pass, fail, infrastructure failure, or invalid artifact.

The minimum acceptable gate for another shadow-mode prototype claim is:

| Metric | Minimum threshold |
|---|---:|
| Valid-schema rate | 99% |
| Escalation recall | 95% |
| Exact match | 80% |
| Critical-human-action escalation accuracy | 100% |
| Required-slice exact match | At least 60% in every required slice |
| Median end-to-end latency | At most 60 seconds |
| p95 end-to-end latency | At most 120 seconds |

The final pre-commitment may be stricter but not weaker. It must also require
Wilson 95% intervals and the numerator/denominator for every rate. Confidence
intervals are interpretation evidence; they do not replace the frozen pass/fail
rule.

Only one candidate may consume the held-out split. Candidate selection must be
complete before the data custodian confirms the final gate commit.

## 11. One-time run and release

The data custodian, not the prompt/model owner, performs the run against the
sealed artifact. Verify every fingerprint before inference.

- Run once, sequentially, with no per-example reruns.
- Do not repair invalid outputs, alter labels, or change thresholds.
- A service interruption before any completed prediction may be classified as
  infrastructure failure under the pre-committed rule.
- Any partial model exposure consumes the split unless the failure rule was
  explicitly frozen otherwise.
- Preserve raw outputs, normalized outputs, timing, environment metadata, and
  complete logs.

Within 72 hours, publish the result whether it passes or fails:

1. the previously sealed manifest and its verified hashes;
2. all v2 held-out ticket text and final labels;
3. raw machine-readable model results;
4. the frozen decision record and gate outcome;
5. agreement and adjudication summaries;
6. slice scores, confidence intervals, and failure analysis;
7. a permanent marker that the v2 held-out split is now consumed.

The prompt/model owner may inspect held-out examples only after this public
release. Any later run is a regression run.

## 12. Evidence required for a prototype claim

Another offline shadow-mode prototype claim is justified only when all of these
are true:

- the collection, labeling, access-separation, seal, and release checklists are
  complete with public evidence;
- every frozen gate passes on the one-time run;
- no required slice is absent or below its gate;
- the result includes uncertainty intervals and does not hide small
  denominators;
- a human reviews every proposed label in the prototype;
- the recommendation states that synthetic evidence does not prove production
  reliability or real-traffic representativeness.

A miss on any gate means the stated prototype claim is rejected. The team may
learn from the failures on a new development version, but it may not tune and
rerun against the consumed v2 held-out split.

## 13. Contributor execution checklist

Copy this checklist into the tracking issue. Every checked item must link to a
commit, artifact, review record, or declaration.

### Protocol and policy

- [ ] Assign the protocol owner and data custodian.
- [ ] Approve this protocol before collecting held-out prose.
- [ ] Write `TASK_V2.md` and resolve every policy item in section 5.
- [ ] Record protocol and policy versions and SHA-256 fingerprints.
- [ ] Confirm no existing test labels or consumed examples were changed.

### Scenario plan and sourcing

- [ ] Create dimension-only scenario cards with no ticket prose or labels.
- [ ] Verify the planned margins and every required slice quota.
- [ ] Recruit at least two writers and record v1 exposure declarations.
- [ ] Collect only original fictional text under the repository license.
- [ ] Scan for personal, customer, employer, secret, and account data.
- [ ] Run duplicate and similarity checks against all v1 tickets.
- [ ] Manually resolve every similarity flag before labeling.

### Labeling

- [ ] Assign two independent reviewers and a separate adjudicator per example.
- [ ] Confirm no reviewer labels a ticket they wrote.
- [ ] Collect policy-cited labels without model outputs.
- [ ] Calculate raw agreement and per-field Cohen's kappa.
- [ ] Pause and revise policy if kappa is below 0.80 or disagreement exceeds 15%.
- [ ] Adjudicate every disagreement and preserve the aggregate log.
- [ ] Re-review affected batches after any policy revision.

### Seal and candidate freeze

- [ ] Canonicalize artifacts and calculate every manifest fingerprint.
- [ ] Verify at least 100 development and 100 held-out examples.
- [ ] Verify marginal balance, slice coverage, source, and license requirements.
- [ ] Store the sealed held-out artifact outside GitHub with access logging.
- [ ] Publish only hashes, counts, aggregates, and declarations.
- [ ] Freeze one candidate, prompt, grader, runner, runtime, and full gate.
- [ ] Confirm the prompt/model owner has not accessed held-out content.

### Run and release

- [ ] Have the custodian verify hashes and execute the frozen command once.
- [ ] Preserve raw results and complete environment metadata.
- [ ] Apply every gate without post-hoc exceptions.
- [ ] Publish pass or failure within 72 hours.
- [ ] Release held-out data, labels, agreement evidence, results, and limitations.
- [ ] Mark v2 held-out as consumed and regression-only.
- [ ] Open follow-up issues without relabeling or rerunning failed examples.

## 14. Stop conditions

Stop and do not make a held-out claim if any of the following occurs:

- a prompt/model owner sees held-out ticket text or labels before release;
- the sealed artifact fingerprint changes without a new version;
- examples are copied from private data or paraphrased from consumed failures;
- labeling independence or adjudication evidence is missing;
- the minimum counts or coverage quotas are not met;
- the gate is changed after any held-out model output exists;
- only passing results are intended for publication.

When a stop condition occurs, document it. The examples may still be released
as a regression batch if licensing and privacy checks pass, but the result must
not be described as held-out generalization.
