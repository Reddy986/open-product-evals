#!/usr/bin/env python3
"""Compare evaluation result JSON files and apply a product decision gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from open_product_evals.reporting import DEFAULT_THRESHOLDS, comparison_markdown


def load_result(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read result {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Result {path} must contain a JSON object")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare model results with an explicit product decision gate."
    )
    parser.add_argument("results", nargs="+", type=Path, help="Result JSON files")
    parser.add_argument("--output", type=Path, help="Write the Markdown report here")
    parser.add_argument(
        "--min-valid-schema",
        type=float,
        default=DEFAULT_THRESHOLDS["valid_schema_rate"],
    )
    parser.add_argument(
        "--min-escalation-recall",
        type=float,
        default=DEFAULT_THRESHOLDS["escalation_recall"],
    )
    parser.add_argument(
        "--min-exact-match",
        type=float,
        default=DEFAULT_THRESHOLDS["exact_match"],
    )
    args = parser.parse_args()

    thresholds = {
        "valid_schema_rate": args.min_valid_schema,
        "escalation_recall": args.min_escalation_recall,
        "exact_match": args.min_exact_match,
    }
    for name, value in thresholds.items():
        if not 0 <= value <= 1:
            parser.error(f"{name} must be between 0 and 1")

    try:
        report = comparison_markdown(
            [load_result(path) for path in args.results], thresholds
        )
    except ValueError as exc:
        parser.error(str(exc))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Report: {args.output}")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()

