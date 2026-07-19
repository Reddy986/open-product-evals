"""Paired analysis for one model evaluated with two prompt variants."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from open_product_evals.scoring import normalize_output


FIELDS = ("category", "priority", "escalate")
FIELD_LABELS = {
    "category": "Category",
    "priority": "Priority",
    "escalate": "Escalation",
}
METRIC_ORDER = (
    "category_accuracy",
    "priority_accuracy",
    "escalation_accuracy",
    "exact_match",
    "valid_schema_rate",
    "escalation_precision",
    "escalation_recall",
)
LATENCY_ORDER = ("mean", "median", "max")


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _metadata(result: Mapping[str, Any], label: str) -> dict[str, Any]:
    evaluation = _mapping(result.get("evaluation"), f"{label} evaluation")
    required = (
        "dataset_sha256",
        "split",
        "selected_examples",
        "prompt_sha256",
        "temperature",
    )
    missing = [name for name in required if name not in evaluation]
    if missing:
        raise ValueError(
            f"{label} evaluation is missing {', '.join(sorted(missing))}"
        )

    model = result.get("model")
    if not isinstance(model, str) or not model:
        raise ValueError(f"{label} model must be a non-empty string")

    try:
        selected_examples = int(evaluation["selected_examples"])
        temperature = float(evaluation["temperature"])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{label} selected_examples and temperature must be numeric"
        ) from exc

    return {
        "model": model,
        "dataset_sha256": str(evaluation["dataset_sha256"]),
        "split": str(evaluation["split"]),
        "selected_examples": selected_examples,
        "prompt_sha256": str(evaluation["prompt_sha256"]),
        "temperature": temperature,
    }


def _records(
    result: Mapping[str, Any], label: str
) -> tuple[list[str], dict[str, Any]]:
    records = result.get("records")
    if not isinstance(records, list):
        raise ValueError(f"{label} records must be a list")

    order: list[str] = []
    by_id: dict[str, Any] = {}
    for record in records:
        row = _mapping(record, f"{label} record")
        identifier = row.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"{label} record IDs must be non-empty strings")
        if identifier in by_id:
            raise ValueError(f"{label} contains duplicate record ID {identifier!r}")
        order.append(identifier)
        by_id[identifier] = row
    return order, by_id


def _numeric_values(
    result: Mapping[str, Any], key: str, label: str
) -> dict[str, float]:
    score = _mapping(result.get("score"), f"{label} score")
    values = _mapping(score.get(key), f"{label} score.{key}")
    numeric: dict[str, float] = {}
    for name, value in values.items():
        try:
            numeric[str(name)] = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} {key}.{name} must be numeric") from exc
    return numeric


def _correctness(record: Mapping[str, Any], label: str) -> dict[str, Any]:
    expected = normalize_output(record.get("expected"))
    if expected is None:
        raise ValueError(f"Invalid expected label for {label}")
    output = normalize_output(record.get("output"))
    correct = {
        field: output is not None and output[field] == expected[field]
        for field in FIELDS
    }
    return {
        "expected": expected,
        "output": output,
        "valid": output is not None,
        "correct": correct,
        "exact": all(correct.values()),
    }


def paired_variant_analysis(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate and compare two prompt variants for the same model and data."""

    baseline_meta = _metadata(baseline, "Baseline")
    candidate_meta = _metadata(candidate, "Candidate")

    compatibility = (
        ("model", "model names differ"),
        ("dataset_sha256", "dataset fingerprints differ"),
        ("split", "splits differ"),
        ("selected_examples", "selected-example counts differ"),
        ("temperature", "temperatures differ"),
    )
    for field, message in compatibility:
        if baseline_meta[field] != candidate_meta[field]:
            raise ValueError(message)

    baseline_order, baseline_records = _records(baseline, "Baseline")
    candidate_order, candidate_records = _records(candidate, "Candidate")
    if set(baseline_order) != set(candidate_order):
        raise ValueError("record ID sets differ")

    selected = baseline_meta["selected_examples"]
    if len(baseline_order) != selected or len(candidate_order) != selected:
        raise ValueError("selected-example count does not match record count")

    for result, label in ((baseline, "Baseline"), (candidate, "Candidate")):
        score = _mapping(result.get("score"), f"{label} score")
        try:
            score_count = int(score["count"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{label} score.count must be numeric") from exc
        if score_count != selected:
            raise ValueError(f"{label} score count does not match selected examples")

    baseline_metrics = _numeric_values(baseline, "metrics", "Baseline")
    candidate_metrics = _numeric_values(candidate, "metrics", "Candidate")
    if set(baseline_metrics) != set(candidate_metrics):
        raise ValueError("metric sets differ")

    baseline_latency = _numeric_values(baseline, "latency_seconds", "Baseline")
    candidate_latency = _numeric_values(candidate, "latency_seconds", "Candidate")
    if set(baseline_latency) != set(candidate_latency):
        raise ValueError("latency metric sets differ")

    exact = {"improved": 0, "regressed": 0}
    fields = {field: {"improved": 0, "regressed": 0} for field in FIELDS}
    identifiers = {
        "exact_improved": [],
        "exact_regressed": [],
        "became_invalid": [],
        "became_valid": [],
    }

    for identifier in baseline_order:
        baseline_state = _correctness(
            baseline_records[identifier], f"baseline record {identifier}"
        )
        candidate_state = _correctness(
            candidate_records[identifier], f"candidate record {identifier}"
        )
        if baseline_state["expected"] != candidate_state["expected"]:
            raise ValueError(f"expected labels differ for record {identifier!r}")

        if not baseline_state["exact"] and candidate_state["exact"]:
            exact["improved"] += 1
            identifiers["exact_improved"].append(identifier)
        elif baseline_state["exact"] and not candidate_state["exact"]:
            exact["regressed"] += 1
            identifiers["exact_regressed"].append(identifier)

        for field in FIELDS:
            baseline_ok = baseline_state["correct"][field]
            candidate_ok = candidate_state["correct"][field]
            if not baseline_ok and candidate_ok:
                fields[field]["improved"] += 1
            elif baseline_ok and not candidate_ok:
                fields[field]["regressed"] += 1

        if baseline_state["valid"] and not candidate_state["valid"]:
            identifiers["became_invalid"].append(identifier)
        elif not baseline_state["valid"] and candidate_state["valid"]:
            identifiers["became_valid"].append(identifier)

    return {
        "metadata": {
            **baseline_meta,
            "baseline_prompt_sha256": baseline_meta["prompt_sha256"],
            "candidate_prompt_sha256": candidate_meta["prompt_sha256"],
        },
        "metrics": {
            name: {
                "baseline": baseline_metrics[name],
                "candidate": candidate_metrics[name],
                "delta": candidate_metrics[name] - baseline_metrics[name],
            }
            for name in baseline_metrics
        },
        "latency_seconds": {
            name: {
                "baseline": baseline_latency[name],
                "candidate": candidate_latency[name],
                "delta": candidate_latency[name] - baseline_latency[name],
            }
            for name in baseline_latency
        },
        "transitions": {
            "exact": exact,
            "fields": fields,
        },
        "identifiers": identifiers,
    }


def _ordered_names(values: Mapping[str, Any], preferred: tuple[str, ...]) -> list[str]:
    return [name for name in preferred if name in values] + sorted(
        name for name in values if name not in preferred
    )


def _identifier_text(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "none"


def paired_variant_markdown(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    baseline_label: str = "Baseline",
    candidate_label: str = "Candidate",
) -> str:
    """Return a deterministic Markdown report for a paired prompt comparison."""

    analysis = paired_variant_analysis(baseline, candidate)
    metadata = analysis["metadata"]
    metrics = analysis["metrics"]
    latency = analysis["latency_seconds"]
    transitions = analysis["transitions"]
    identifiers = analysis["identifiers"]

    lines = [
        "# Paired prompt-variant comparison",
        "",
        f"- **Model:** `{metadata['model']}`",
        f"- **Split:** `{metadata['split']}` ({metadata['selected_examples']} examples)",
        f"- **Dataset SHA-256:** `{metadata['dataset_sha256']}`",
        f"- **Temperature:** {metadata['temperature']:g}",
        f"- **{baseline_label} prompt SHA-256:** `{metadata['baseline_prompt_sha256']}`",
        f"- **{candidate_label} prompt SHA-256:** `{metadata['candidate_prompt_sha256']}`",
        "",
        "## Metric deltas",
        "",
        f"| Metric | {baseline_label} | {candidate_label} | Delta |",
        "|---|---:|---:|---:|",
    ]
    for name in _ordered_names(metrics, METRIC_ORDER):
        values = metrics[name]
        lines.append(
            f"| {name.replace('_', ' ').title()} | "
            f"{values['baseline']:.1%} | {values['candidate']:.1%} | "
            f"{values['delta'] * 100:+.1f} pp |"
        )

    lines.extend(
        [
            "",
            "## Latency deltas",
            "",
            f"| Statistic | {baseline_label} | {candidate_label} | Delta |",
            "|---|---:|---:|---:|",
        ]
    )
    for name in _ordered_names(latency, LATENCY_ORDER):
        values = latency[name]
        lines.append(
            f"| {name.title()} | {values['baseline']:.2f}s | "
            f"{values['candidate']:.2f}s | {values['delta']:+.2f}s |"
        )

    lines.extend(
        [
            "",
            "## Paired transitions",
            "",
            "| Decision | Improved | Regressed | Net |",
            "|---|---:|---:|---:|",
            f"| Exact match | {transitions['exact']['improved']} | "
            f"{transitions['exact']['regressed']} | "
            f"{transitions['exact']['improved'] - transitions['exact']['regressed']:+d} |",
        ]
    )
    for field in FIELDS:
        values = transitions["fields"][field]
        lines.append(
            f"| {FIELD_LABELS[field]} | {values['improved']} | "
            f"{values['regressed']} | "
            f"{values['improved'] - values['regressed']:+d} |"
        )

    lines.extend(
        [
            "",
            "## Example transitions",
            "",
            f"- **Exact improvements:** {_identifier_text(identifiers['exact_improved'])}",
            f"- **Exact regressions:** {_identifier_text(identifiers['exact_regressed'])}",
            f"- **Became invalid:** {_identifier_text(identifiers['became_invalid'])}",
            f"- **Became valid:** {_identifier_text(identifiers['became_valid'])}",
            "",
            "> A paired development-set change shows regression behavior for these examples. "
            "It does not establish generalization, statistical significance, or production readiness.",
            "",
        ]
    )
    return "\n".join(lines)
