#!/usr/bin/env python3
"""Create and compare blind human response-quality annotations."""

from __future__ import annotations

import argparse
from pathlib import Path

from open_product_evals.calibration import (
    build_annotation_template,
    compare_annotations,
    read_jsonl,
    render_calibration_markdown,
    validate_calibration_dataset,
    write_jsonl,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the dependency-free human rubric-calibration workflow."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    initialize = subparsers.add_parser(
        "init", help="Create a blank annotation sheet for one reviewer."
    )
    initialize.add_argument("--dataset", required=True, type=Path)
    initialize.add_argument("--reviewer", required=True)
    initialize.add_argument("--output", required=True, type=Path)

    compare = subparsers.add_parser(
        "compare", help="Compare two complete, independent annotation sheets."
    )
    compare.add_argument("reviewer_a", type=Path)
    compare.add_argument("reviewer_b", type=Path)
    compare.add_argument("--output", required=True, type=Path)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "init":
            dataset = validate_calibration_dataset(read_jsonl(args.dataset))
            template = build_annotation_template(dataset, args.reviewer)
            write_jsonl(template, args.output)
            print(
                f"Created {len(template)} blind annotations for {args.reviewer}; "
                f"dataset {template[0]['dataset_fingerprint']}: {args.output}"
            )
            return

        reviewer_a = read_jsonl(args.reviewer_a)
        reviewer_b = read_jsonl(args.reviewer_b)
        comparison = compare_annotations(reviewer_a, reviewer_b)
        report = render_calibration_markdown(comparison)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(report)
        status = "PASS" if comparison["calibration_gate_passed"] else "FAIL"
        print(
            f"Compared {comparison['example_count']} examples: calibration gate {status}; "
            f"report: {args.output}"
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
