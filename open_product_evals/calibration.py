"""Human rubric-calibration helpers for response-quality evaluations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


DIMENSIONS = (
    "correctness",
    "policy_safety",
    "actionability",
    "communication",
)
SCORE_MIN = 1
SCORE_MAX = 4
MIN_QUADRATIC_WEIGHTED_KAPPA = 0.60
MAX_MEAN_ABSOLUTE_DIFFERENCE = 0.50
MIN_CRITICAL_FAILURE_AGREEMENT = 0.90
MIN_CRITICAL_FAILURE_POSITIVES_PER_REVIEWER = 2
MIN_CRITICAL_FAILURE_NEGATIVES_PER_REVIEWER = 2
RUBRIC_VERSION = "v0.3-draft-1"


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read a non-empty JSONL file and report line-specific errors."""

    records: list[dict[str, Any]] = []
    source = Path(path)
    with source.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{source}:{line_number}: invalid JSON: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(f"{source}:{line_number}: expected a JSON object")
            records.append(record)
    if not records:
        raise ValueError(f"{source}: expected at least one JSONL record")
    return records


def validate_calibration_dataset(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate the public, unlabeled response-quality calibration set."""

    validated = list(records)
    seen_ids: set[str] = set()
    for index, record in enumerate(validated, start=1):
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id.startswith("rq-cal-"):
            raise ValueError(f"record {index}: id must start with 'rq-cal-'")
        if record_id in seen_ids:
            raise ValueError(f"duplicate dataset id: {record_id}")
        seen_ids.add(record_id)

        if record.get("split") != "calibration":
            raise ValueError(f"{record_id}: split must be 'calibration'")
        for field in ("ticket", "draft_response"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"{record_id}: {field} must be a non-empty string")
        slices = record.get("slices")
        if (
            not isinstance(slices, list)
            or not slices
            or any(not isinstance(value, str) or not value for value in slices)
        ):
            raise ValueError(f"{record_id}: slices must be a non-empty string list")
        forbidden = {"scores", "critical_failure", "expected", "gold"}
        leaked = forbidden.intersection(record)
        if leaked:
            raise ValueError(
                f"{record_id}: public calibration data must not contain labels: "
                + ", ".join(sorted(leaked))
            )
    return validated


def fingerprint_dataset(records: Iterable[dict[str, Any]]) -> str:
    """Fingerprint validated records in their presented annotation order."""

    dataset = validate_calibration_dataset(records)
    canonical_lines = [
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in dataset
    ]
    payload = ("\n".join(canonical_lines) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_annotation_template(
    dataset_records: Iterable[dict[str, Any]], reviewer: str
) -> list[dict[str, Any]]:
    """Create a blank, reviewer-specific annotation sheet."""

    reviewer_id = reviewer.strip()
    if not reviewer_id:
        raise ValueError("reviewer must be non-empty")
    dataset = validate_calibration_dataset(dataset_records)
    dataset_fingerprint = fingerprint_dataset(dataset)
    return [
        {
            "id": record["id"],
            "reviewer": reviewer_id,
            "dataset_fingerprint": dataset_fingerprint,
            "rubric_version": RUBRIC_VERSION,
            "scores": {dimension: None for dimension in DIMENSIONS},
            "critical_failure": None,
            "notes": "",
        }
        for record in dataset
    ]


def write_jsonl(
    records: Iterable[dict[str, Any]], path: str | Path, *, overwrite: bool = False
) -> None:
    """Write JSONL without silently replacing an existing review."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if overwrite else "x"
    with output.open(mode, encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def validate_annotations(
    records: Iterable[dict[str, Any]], *, require_complete: bool = True
) -> tuple[str, str, str, dict[str, dict[str, Any]]]:
    """Validate one reviewer's annotations and index them by example id."""

    annotations = list(records)
    if not annotations:
        raise ValueError("expected at least one annotation")

    reviewers: set[str] = set()
    dataset_fingerprints: set[str] = set()
    rubric_versions: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(annotations, start=1):
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError(f"annotation {index}: id must be a non-empty string")
        if record_id in by_id:
            raise ValueError(f"duplicate annotation id: {record_id}")

        reviewer = record.get("reviewer")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError(f"{record_id}: reviewer must be a non-empty string")
        reviewers.add(reviewer.strip())

        dataset_fingerprint = record.get("dataset_fingerprint")
        if (
            not isinstance(dataset_fingerprint, str)
            or len(dataset_fingerprint) != 64
            or any(character not in "0123456789abcdef" for character in dataset_fingerprint)
        ):
            raise ValueError(f"{record_id}: dataset_fingerprint must be lowercase SHA-256")
        dataset_fingerprints.add(dataset_fingerprint)

        rubric_version = record.get("rubric_version")
        if not isinstance(rubric_version, str) or not rubric_version.strip():
            raise ValueError(f"{record_id}: rubric_version must be a non-empty string")
        rubric_versions.add(rubric_version.strip())

        scores = record.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(DIMENSIONS):
            raise ValueError(
                f"{record_id}: scores must contain exactly {', '.join(DIMENSIONS)}"
            )
        for dimension in DIMENSIONS:
            value = scores[dimension]
            if value is None and not require_complete:
                continue
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{record_id}: {dimension} must be an integer")
            if not SCORE_MIN <= value <= SCORE_MAX:
                raise ValueError(
                    f"{record_id}: {dimension} must be {SCORE_MIN}-{SCORE_MAX}"
                )

        critical_failure = record.get("critical_failure")
        if critical_failure is None and not require_complete:
            pass
        elif not isinstance(critical_failure, bool):
            raise ValueError(f"{record_id}: critical_failure must be true or false")

        notes = record.get("notes", "")
        if not isinstance(notes, str):
            raise ValueError(f"{record_id}: notes must be a string")
        by_id[record_id] = record

    if len(reviewers) != 1:
        raise ValueError("each annotation file must contain exactly one reviewer")
    if len(dataset_fingerprints) != 1:
        raise ValueError("each annotation file must contain one dataset fingerprint")
    if len(rubric_versions) != 1:
        raise ValueError("each annotation file must contain one rubric version")
    return (
        next(iter(reviewers)),
        next(iter(dataset_fingerprints)),
        next(iter(rubric_versions)),
        by_id,
    )


def quadratic_weighted_kappa(
    values_a: list[int], values_b: list[int], *, minimum: int = 1, maximum: int = 4
) -> float | None:
    """Compute quadratic weighted Cohen's kappa for ordinal scores."""

    if not values_a or len(values_a) != len(values_b):
        raise ValueError("kappa inputs must be non-empty and have equal length")
    if maximum <= minimum:
        raise ValueError("maximum must be greater than minimum")
    allowed = range(minimum, maximum + 1)
    if any(value not in allowed for value in values_a + values_b):
        raise ValueError("kappa values are outside the configured score range")

    size = maximum - minimum + 1
    observed = [[0 for _ in range(size)] for _ in range(size)]
    rows = [0 for _ in range(size)]
    columns = [0 for _ in range(size)]
    for value_a, value_b in zip(values_a, values_b):
        row = value_a - minimum
        column = value_b - minimum
        observed[row][column] += 1
        rows[row] += 1
        columns[column] += 1

    count = len(values_a)
    denominator = float((size - 1) ** 2)
    observed_disagreement = 0.0
    expected_disagreement = 0.0
    for row in range(size):
        for column in range(size):
            weight = ((row - column) ** 2) / denominator
            observed_disagreement += weight * observed[row][column] / count
            expected_disagreement += (
                weight * rows[row] * columns[column] / (count * count)
            )

    if expected_disagreement == 0:
        # Kappa is undefined when both reviewers use one identical category.
        # Treating that degenerate case as perfect reliability can hide a rubric
        # that never exercised its ordinal distinctions.
        return None
    return 1.0 - (observed_disagreement / expected_disagreement)


def compare_annotations(
    records_a: Iterable[dict[str, Any]], records_b: Iterable[dict[str, Any]]
) -> dict[str, Any]:
    """Compare two independent, complete annotation files."""

    reviewer_a, fingerprint_a, rubric_a, annotations_a = validate_annotations(records_a)
    reviewer_b, fingerprint_b, rubric_b, annotations_b = validate_annotations(records_b)
    if reviewer_a == reviewer_b:
        raise ValueError("reviewer ids must differ for independent calibration")
    if fingerprint_a != fingerprint_b:
        raise ValueError("annotation dataset fingerprints differ")
    if rubric_a != rubric_b:
        raise ValueError("annotation rubric versions differ")
    if set(annotations_a) != set(annotations_b):
        missing_from_b = sorted(set(annotations_a) - set(annotations_b))
        missing_from_a = sorted(set(annotations_b) - set(annotations_a))
        details = []
        if missing_from_b:
            details.append("missing from reviewer B: " + ", ".join(missing_from_b))
        if missing_from_a:
            details.append("missing from reviewer A: " + ", ".join(missing_from_a))
        raise ValueError("annotation id sets differ; " + "; ".join(details))

    record_ids = list(annotations_a)
    dimension_metrics: dict[str, dict[str, Any]] = {}
    for dimension in DIMENSIONS:
        values_a = [annotations_a[record_id]["scores"][dimension] for record_id in record_ids]
        values_b = [annotations_b[record_id]["scores"][dimension] for record_id in record_ids]
        differences = [abs(a - b) for a, b in zip(values_a, values_b)]
        exact_agreement = sum(a == b for a, b in zip(values_a, values_b)) / len(record_ids)
        adjacent_agreement = sum(diff <= 1 for diff in differences) / len(record_ids)
        mean_absolute_difference = sum(differences) / len(record_ids)
        kappa = quadratic_weighted_kappa(values_a, values_b)
        dimension_metrics[dimension] = {
            "exact_agreement": exact_agreement,
            "adjacent_agreement": adjacent_agreement,
            "mean_absolute_difference": mean_absolute_difference,
            "quadratic_weighted_kappa": kappa,
            "reviewer_a_distribution": {
                score: values_a.count(score) for score in range(SCORE_MIN, SCORE_MAX + 1)
            },
            "reviewer_b_distribution": {
                score: values_b.count(score) for score in range(SCORE_MIN, SCORE_MAX + 1)
            },
            "gate_passed": (
                kappa is not None
                and kappa >= MIN_QUADRATIC_WEIGHTED_KAPPA
                and mean_absolute_difference <= MAX_MEAN_ABSOLUTE_DIFFERENCE
            ),
        }

    critical_a = [annotations_a[record_id]["critical_failure"] for record_id in record_ids]
    critical_b = [annotations_b[record_id]["critical_failure"] for record_id in record_ids]
    critical_agreement = sum(a == b for a, b in zip(critical_a, critical_b)) / len(record_ids)
    both_positive = sum(a and b for a, b in zip(critical_a, critical_b))
    positive_calls = sum(critical_a) + sum(critical_b)
    positive_agreement = None if positive_calls == 0 else (2 * both_positive / positive_calls)

    disagreements = []
    for record_id in record_ids:
        annotation_a = annotations_a[record_id]
        annotation_b = annotations_b[record_id]
        score_differences = {
            dimension: abs(
                annotation_a["scores"][dimension]
                - annotation_b["scores"][dimension]
            )
            for dimension in DIMENSIONS
        }
        critical_mismatch = (
            annotation_a["critical_failure"] != annotation_b["critical_failure"]
        )
        if critical_mismatch or any(score_differences.values()):
            disagreements.append(
                {
                    "id": record_id,
                    "critical_mismatch": critical_mismatch,
                    "max_score_difference": max(score_differences.values()),
                    "score_differences": score_differences,
                    "reviewer_a_scores": annotation_a["scores"],
                    "reviewer_b_scores": annotation_b["scores"],
                    "reviewer_a_critical": annotation_a["critical_failure"],
                    "reviewer_b_critical": annotation_b["critical_failure"],
                }
            )
    disagreements.sort(
        key=lambda item: (
            not item["critical_mismatch"],
            -item["max_score_difference"],
            item["id"],
        )
    )

    critical_coverage_passed = (
        sum(critical_a) >= MIN_CRITICAL_FAILURE_POSITIVES_PER_REVIEWER
        and sum(critical_b) >= MIN_CRITICAL_FAILURE_POSITIVES_PER_REVIEWER
        and len(critical_a) - sum(critical_a) >= MIN_CRITICAL_FAILURE_NEGATIVES_PER_REVIEWER
        and len(critical_b) - sum(critical_b) >= MIN_CRITICAL_FAILURE_NEGATIVES_PER_REVIEWER
    )
    critical_gate_passed = (
        critical_agreement >= MIN_CRITICAL_FAILURE_AGREEMENT
        and critical_coverage_passed
    )
    calibration_gate_passed = critical_gate_passed and all(
        metrics["gate_passed"] for metrics in dimension_metrics.values()
    )
    return {
        "reviewer_a": reviewer_a,
        "reviewer_b": reviewer_b,
        "dataset_fingerprint": fingerprint_a,
        "rubric_version": rubric_a,
        "example_count": len(record_ids),
        "dimensions": dimension_metrics,
        "critical_failure": {
            "exact_agreement": critical_agreement,
            "positive_agreement": positive_agreement,
            "reviewer_a_positive_count": sum(critical_a),
            "reviewer_b_positive_count": sum(critical_b),
            "coverage_gate_passed": critical_coverage_passed,
            "gate_passed": critical_gate_passed,
        },
        "disagreements": disagreements,
        "calibration_gate_passed": calibration_gate_passed,
    }


def render_calibration_markdown(comparison: dict[str, Any]) -> str:
    """Render an inspectable human-human calibration report."""

    status = "PASS" if comparison["calibration_gate_passed"] else "FAIL"
    lines = [
        "# Human rubric calibration report",
        "",
        "> This report measures human-human agreement. It does not validate an LLM judge.",
        "",
        f"- Reviewer A: `{comparison['reviewer_a']}`",
        f"- Reviewer B: `{comparison['reviewer_b']}`",
        f"- Dataset SHA-256: `{comparison['dataset_fingerprint']}`",
        f"- Rubric version: `{comparison['rubric_version']}`",
        f"- Shared examples: {comparison['example_count']}",
        f"- Pre-committed calibration gate: **{status}**",
        "",
        "## Dimension agreement",
        "",
        "| Dimension | Exact | Within 1 point | Mean absolute difference | Quadratic weighted κ | Gate |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    for dimension in DIMENSIONS:
        metrics = comparison["dimensions"][dimension]
        gate = "PASS" if metrics["gate_passed"] else "FAIL"
        kappa_display = (
            "undefined"
            if metrics["quadratic_weighted_kappa"] is None
            else f"{metrics['quadratic_weighted_kappa']:.3f}"
        )
        lines.append(
            f"| {dimension.replace('_', ' ').title()} "
            f"| {metrics['exact_agreement']:.1%} "
            f"| {metrics['adjacent_agreement']:.1%} "
            f"| {metrics['mean_absolute_difference']:.2f} "
            f"| {kappa_display} | {gate} |"
        )

    lines.extend(
        [
            "",
            "### Score distributions",
            "",
            "| Dimension | Reviewer A counts (1/2/3/4) | Reviewer B counts (1/2/3/4) |",
            "|---|---:|---:|",
        ]
    )
    for dimension in DIMENSIONS:
        metrics = comparison["dimensions"][dimension]
        distribution_a = "/".join(
            str(metrics["reviewer_a_distribution"][score])
            for score in range(SCORE_MIN, SCORE_MAX + 1)
        )
        distribution_b = "/".join(
            str(metrics["reviewer_b_distribution"][score])
            for score in range(SCORE_MIN, SCORE_MAX + 1)
        )
        lines.append(
            f"| {dimension.replace('_', ' ').title()} | {distribution_a} | {distribution_b} |"
        )

    critical = comparison["critical_failure"]
    critical_gate = "PASS" if critical["gate_passed"] else "FAIL"
    positive_agreement_display = (
        "n/a"
        if critical["positive_agreement"] is None
        else f"{critical['positive_agreement']:.1%}"
    )
    lines.extend(
        [
            "",
            "## Critical-failure agreement",
            "",
            "| Exact agreement | Positive agreement | Reviewer A positives | Reviewer B positives | Gate |",
            "|---:|---:|---:|---:|:---:|",
            f"| {critical['exact_agreement']:.1%} "
            f"| {positive_agreement_display} "
            f"| {critical['reviewer_a_positive_count']} "
            f"| {critical['reviewer_b_positive_count']} | {critical_gate} |",
            "",
            "## Pre-committed gates",
            "",
            f"- Quadratic weighted κ must be at least {MIN_QUADRATIC_WEIGHTED_KAPPA:.2f} for every dimension.",
            f"- Mean absolute difference must be at most {MAX_MEAN_ABSOLUTE_DIFFERENCE:.2f} for every dimension.",
            f"- Critical-failure exact agreement must be at least {MIN_CRITICAL_FAILURE_AGREEMENT:.0%}.",
            f"- Each reviewer must assign at least {MIN_CRITICAL_FAILURE_POSITIVES_PER_REVIEWER} positive and {MIN_CRITICAL_FAILURE_NEGATIVES_PER_REVIEWER} negative critical-failure labels so a constant review cannot pass.",
            "- Passing these gates is necessary but not sufficient: adjudicate every disagreement before calibrating a model judge.",
            "",
            "## Disagreements to adjudicate",
            "",
        ]
    )
    if not comparison["disagreements"]:
        lines.append("No disagreements.")
    else:
        lines.extend(
            [
                "| ID | Critical mismatch | Largest score gap | Differing dimensions |",
                "|---|:---:|---:|---|",
            ]
        )
        for disagreement in comparison["disagreements"]:
            differing_dimensions = [
                f"{dimension}: {disagreement['reviewer_a_scores'][dimension]}→{disagreement['reviewer_b_scores'][dimension]}"
                for dimension, difference in disagreement["score_differences"].items()
                if difference
            ]
            if disagreement["critical_mismatch"]:
                differing_dimensions.append(
                    "critical: "
                    f"{str(disagreement['reviewer_a_critical']).lower()}→"
                    f"{str(disagreement['reviewer_b_critical']).lower()}"
                )
            lines.append(
                f"| `{disagreement['id']}` "
                f"| {'yes' if disagreement['critical_mismatch'] else 'no'} "
                f"| {disagreement['max_score_difference']} "
                f"| {', '.join(differing_dimensions)} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation limit",
            "",
            "This small public calibration set is a rubric-debugging exercise. It is not a held-out judge benchmark, and agreement on it does not establish model-judge validity or production readiness.",
            "",
        ]
    )
    return "\n".join(lines)
