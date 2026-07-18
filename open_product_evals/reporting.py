"""Comparison and decision-gate reporting for evaluation results."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


DEFAULT_THRESHOLDS = {
    "valid_schema_rate": 0.95,
    "escalation_recall": 0.90,
    "exact_match": 0.70,
}


def evaluate_gate(
    result: Mapping[str, Any],
    thresholds: Mapping[str, float] = DEFAULT_THRESHOLDS,
) -> dict[str, Any]:
    """Evaluate a result against an explicit, risk-first product gate."""

    try:
        metrics = result["score"]["metrics"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Result is missing score.metrics") from exc

    checks = {}
    for metric, threshold in thresholds.items():
        if metric not in metrics:
            raise ValueError(f"Result is missing required metric {metric!r}")
        actual = float(metrics[metric])
        checks[metric] = {
            "actual": actual,
            "threshold": threshold,
            "passed": actual >= threshold,
        }

    return {
        "passed": all(check["passed"] for check in checks.values()),
        "checks": checks,
    }


def _percent(value: float) -> str:
    return f"{value:.1%}"


def _top_errors(result: Mapping[str, Any], limit: int = 3) -> str:
    summary = result.get("score", {}).get("error_summary", {})
    ranked = sorted(summary.items(), key=lambda item: (-item[1], item[0]))
    if not ranked:
        return "none"
    return ", ".join(f"{name.replace('_', ' ')} ({count})" for name, count in ranked[:limit])


def comparison_markdown(
    results: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float] = DEFAULT_THRESHOLDS,
) -> str:
    """Return a compact Markdown report for one or more result files."""

    if not results:
        raise ValueError("At least one result is required")

    fingerprints = {
        (
            result.get("evaluation", {}).get("dataset_sha256"),
            result.get("evaluation", {}).get("split"),
            result.get("evaluation", {}).get("selected_examples"),
        )
        for result in results
        if result.get("evaluation", {}).get("dataset_sha256")
    }
    if len(fingerprints) > 1:
        raise ValueError(
            "Results use different dataset fingerprints, splits, or example counts"
        )

    lines = [
        "# Evaluation comparison",
        "",
        "| Candidate | Examples | Valid schema | Escalation recall | Exact match | Median latency | Gate |",
        "|---|---:|---:|---:|---:|---:|:---:|",
    ]
    gates = []
    for result in results:
        try:
            model = str(result["model"])
            score = result["score"]
            metrics = score["metrics"]
            count = int(score["count"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid evaluation result") from exc
        gate = evaluate_gate(result, thresholds)
        gates.append((model, gate))
        latency = score.get("latency_seconds", {}).get("median")
        latency_text = f"{float(latency):.2f}s" if latency is not None else "n/a"
        lines.append(
            "| "
            + " | ".join(
                [
                    model.replace("|", "\\|"),
                    str(count),
                    _percent(float(metrics["valid_schema_rate"])),
                    _percent(float(metrics["escalation_recall"])),
                    _percent(float(metrics["exact_match"])),
                    latency_text,
                    "PASS" if gate["passed"] else "FAIL",
                ]
            )
            + " |"
        )

    lines.extend(["", "## Gate definition", ""])
    for metric, threshold in thresholds.items():
        lines.append(f"- `{metric}` ≥ {_percent(threshold)}")

    lines.extend(
        [
            "",
            "This gate is a worked product hypothesis, not a production-safety certification. "
            "The public synthetic test set is too small to establish production reliability.",
            "",
            "## Failure patterns",
            "",
        ]
    )
    for result in results:
        lines.append(f"- **{result['model']}**: {_top_errors(result)}")

    failed_details = []
    for model, gate in gates:
        for metric, check in gate["checks"].items():
            if not check["passed"]:
                failed_details.append(
                    f"- **{model}** misses `{metric}`: "
                    f"{_percent(check['actual'])} vs {_percent(check['threshold'])}."
                )
    if failed_details:
        lines.extend(["", "## Gate misses", "", *failed_details])

    lines.extend(
        [
            "",
            "## Interpretation checklist",
            "",
            "- Inspect individual failures before changing the prompt.",
            "- Iterate on the development split; reserve the test split for comparison.",
            "- Treat small score differences as inconclusive until repeated trials or uncertainty estimates are available.",
            "- Revisit the gate when the product cost of false positives or false negatives changes.",
            "",
        ]
    )
    return "\n".join(lines)
