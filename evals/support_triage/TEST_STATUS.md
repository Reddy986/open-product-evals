# Test split status

## Current status: consumed

The 20-example test split was first sent to a model on July 18, 2026 after the
prompt, Qwen3 model revision, and product gate were frozen in a public
pre-commitment.

- Candidate: `qwen3:4b`, Ollama ID `359d7dd4bcda`
- Prompt SHA-256:
  `9e1afd232a800aefb723984684d1b1aefc677a730feda13023c4d04b09f22f7b`
- Dataset SHA-256:
  `d299f565faf9c7249e5164d75f16cd4f5be781235556fc108bbf7cbf3b5522c9`
- Decision: failed because exact match was 60.0% against a 70.0% threshold
- Evidence:
  [held-out decision record](../../results/published/2026-07-18-qwen3-v1-held-out/README.md)

## How to use it now

The split remains useful as a transparent regression suite. It is no longer a
pristine held-out set for prompt or policy decisions informed by the published
failures.

- You may reproduce the published run or compare a separately selected model.
- Do not tune a prompt on these examples and then call the resulting score
  held-out performance.
- If the labels or policy change in response to test failures, version the
  dataset and collect a new test split before making another held-out claim.
- Record any prior exposure when publishing future results.

This marker is intentionally permanent. A test set does not become unseen again
because time passes or a new prompt is written.

The design for a genuinely new held-out collection is documented in
[DATASET_V2_PROTOCOL.md](DATASET_V2_PROTOCOL.md). That protocol currently
contains no v2 ticket text or labels; collection begins only after its policy
and access-separation requirements can be met.
