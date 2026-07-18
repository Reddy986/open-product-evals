"""Deterministic scoring for the support-triage evaluation."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


ALLOWED_CATEGORIES = {
    "billing",
    "account_access",
    "technical_issue",
    "feature_request",
    "general_question",
}
ALLOWED_PRIORITIES = {"low", "medium", "high", "urgent"}


def normalize_output(value: Any) -> dict[str, Any] | None:
    """Return a canonical prediction, or ``None`` when the schema is invalid."""

    if not isinstance(value, dict):
        return None

    category = value.get("category")
    priority = value.get("priority")
    escalate = value.get("escalate")

    if not isinstance(category, str) or not isinstance(priority, str):
        return None
    category = category.strip().lower()
    priority = priority.strip().lower()

    if category not in ALLOWED_CATEGORIES:
        return None
    if priority not in ALLOWED_PRIORITIES:
        return None
    if not isinstance(escalate, bool):
        return None

    return {
        "category": category,
        "priority": priority,
        "escalate": escalate,
    }


def _safe_ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def score_records(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Score records containing ``expected``, ``output`` and optional ``slices``."""

    rows = list(records)
    if not rows:
        raise ValueError("At least one record is required")

    totals = defaultdict(int)
    per_slice: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "exact": 0})
    failures: list[dict[str, Any]] = []

    for row in rows:
        expected = normalize_output(row.get("expected"))
        if expected is None:
            raise ValueError(f"Invalid expected label for {row.get('id', '<unknown>')}")

        output = normalize_output(row.get("output"))
        valid = output is not None
        totals["valid"] += int(valid)

        category_ok = valid and output["category"] == expected["category"]
        priority_ok = valid and output["priority"] == expected["priority"]
        escalation_ok = valid and output["escalate"] == expected["escalate"]
        exact = category_ok and priority_ok and escalation_ok

        totals["category"] += int(category_ok)
        totals["priority"] += int(priority_ok)
        totals["escalation"] += int(escalation_ok)
        totals["exact"] += int(exact)

        predicted_escalation = bool(output and output["escalate"])
        if predicted_escalation and expected["escalate"]:
            totals["tp"] += 1
        elif predicted_escalation and not expected["escalate"]:
            totals["fp"] += 1
        elif not predicted_escalation and expected["escalate"]:
            totals["fn"] += 1

        for slice_name in row.get("slices", []):
            per_slice[slice_name]["total"] += 1
            per_slice[slice_name]["exact"] += int(exact)

        if not exact:
            failures.append(
                {
                    "id": row.get("id"),
                    "expected": expected,
                    "output": output,
                    "valid_schema": valid,
                }
            )

    count = len(rows)
    precision = _safe_ratio(totals["tp"], totals["tp"] + totals["fp"])
    recall = _safe_ratio(totals["tp"], totals["tp"] + totals["fn"])

    return {
        "count": count,
        "metrics": {
            "category_accuracy": _safe_ratio(totals["category"], count),
            "priority_accuracy": _safe_ratio(totals["priority"], count),
            "escalation_accuracy": _safe_ratio(totals["escalation"], count),
            "exact_match": _safe_ratio(totals["exact"], count),
            "valid_schema_rate": _safe_ratio(totals["valid"], count),
            "escalation_precision": precision,
            "escalation_recall": recall,
        },
        "slices": {
            name: {
                "count": values["total"],
                "exact_match": _safe_ratio(values["exact"], values["total"]),
            }
            for name, values in sorted(per_slice.items())
        },
        "failures": failures,
    }

