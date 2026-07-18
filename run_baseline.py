#!/usr/bin/env python3
"""Run the transparent, zero-dependency keyword baseline."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from open_product_evals.baseline import predict
from open_product_evals.scoring import score_records
from run_eval import DEFAULT_DATASET, file_sha256, load_dataset, print_summary


ROOT = Path(__file__).resolve().parent


def run_baseline(dataset: list[dict[str, Any]]) -> dict[str, Any]:
    records = [
        {
            "id": example["id"],
            "ticket": example["ticket"],
            "expected": example["expected"],
            "output": predict(example["ticket"]),
            "slices": example.get("slices", []),
            "latency_seconds": 0.0,
        }
        for example in dataset
    ]
    score = score_records(records)
    score["latency_seconds"] = {"mean": 0.0, "median": 0.0, "max": 0.0}
    return {
        "model": "keyword-baseline-v1 (not an LLM)",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "score": score,
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the transparent keyword baseline without a model runtime."
    )
    parser.add_argument(
        "--split", choices=["development", "test", "all"], default="development"
    )
    parser.add_argument("--limit", type=int, help="Run only the first N examples")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument(
        "--output", type=Path, help="Optional path for the machine-readable result"
    )
    args = parser.parse_args()

    dataset = load_dataset(args.dataset, args.split)
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit must be at least 1")
        dataset = dataset[: args.limit]

    result = run_baseline(dataset)
    result["evaluation"] = {
        "split": args.split,
        "selected_examples": len(dataset),
        "dataset_path": str(args.dataset),
        "dataset_sha256": file_sha256(args.dataset),
        "prompt_path": None,
        "prompt_sha256": None,
        "temperature": None,
    }
    print_summary(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"Full result: {args.output}")


if __name__ == "__main__":
    main()
