# Support-ticket triage

## Product decision

Can a small, locally running open-weight model reliably route support tickets and identify cases requiring human attention?

## Unit of evaluation

One fictional customer-support message. The model returns a category, a priority, and an escalation decision.

## Labels

### Category

- `billing`: charges, invoices, refunds, payments, subscriptions, or pricing
- `account_access`: authentication, security, account ownership, verification, or deletion
- `technical_issue`: broken or degraded product behavior
- `feature_request`: requested new or expanded functionality
- `general_question`: documentation, policies, availability, partnerships, or anything else

### Priority

- `urgent`: compromise, outage, missing critical data, or immediate privacy/safety risk
- `high`: disputed money, blocked access, stopped work, or time-sensitive human action
- `medium`: meaningful friction with a workaround or a non-urgent change
- `low`: information, cosmetic issues, or optional suggestions

### Escalation

`true` means a human must act or investigate. Typical examples include refunds, disputed charges, compromised accounts, privacy requests, missing data, outages, and requests outside self-service support.

## Metrics

- Category accuracy
- Priority accuracy
- Escalation accuracy
- Escalation precision and recall
- Exact-match accuracy across all three fields
- Valid-schema rate
- Exact-match accuracy by behavioral slice
- Category, priority, escalation, and schema accuracy by behavioral slice
- Failure counts for invalid schemas, routing errors, priority errors, missed escalations, and unnecessary escalations

Escalation recall is the most important first-release metric because a false negative can leave a risky or time-sensitive case unattended.

## Worked decision gate

The comparison report uses an illustrative gate of 95% valid schemas, 90%
escalation recall, and 70% exact match. These are hypotheses chosen to make the
product decision explicit; they are not a production-safety certification. The
public synthetic test set is too small to demonstrate production reliability.

## Dataset

The dataset contains 60 manually reviewed, synthetic English-language tickets: 40 development examples and 20 test examples. It contains no customer or employer data.

## Limitations

- The taxonomy is intentionally small and fictional.
- The examples are synthetic and may not reflect real traffic distributions.
- The public test labels make this appropriate for learning and regression testing, not a contamination-resistant leaderboard.
- The evaluation does not measure response quality, multi-turn resolution, safety beyond the included escalation policy, or production reliability.
