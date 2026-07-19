#!/usr/bin/env python3
"""Compare one model across two prompt variants on the same examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from open_product_evals.variants import paired_variant_markdown


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
        description="Compare one model across two compatible prompt variants."
    )
    parser.add_argument("baseline", type=Path, help="Baseline result JSON")
    parser.add_argument("candidate", type=Path, help="Candidate result JSON")
    parser.add_argument("--baseline-label", default="Baseline")
    parser.add_argument("--candidate-label", default="Candidate")
    parser.add_argument("--output", type=Path, help="Write the Markdown report here")
    args = parser.parse_args()

    try:
        report = paired_variant_markdown(
            load_result(args.baseline),
            load_result(args.candidate),
            baseline_label=args.baseline_label,
            candidate_label=args.candidate_label,
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
