#!/usr/bin/env python3
"""Run the support-triage evaluation against one or more Ollama models."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from open_product_evals.ollama import OllamaError, generate_json
from open_product_evals.scoring import score_records


ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = ROOT / "evals" / "support_triage" / "dataset.jsonl"
DEFAULT_PROMPT = ROOT / "evals" / "support_triage" / "prompt.txt"


def load_dataset(path: Path, split: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if split == "all" or row.get("split") == split:
                rows.append(row)
            if "id" not in row or "ticket" not in row or "expected" not in row:
                raise ValueError(f"Missing required field on line {line_number}")
    if not rows:
        raise ValueError(f"No examples found for split {split!r}")
    return rows


def model_slug(model: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", model).strip("-")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def portable_path(path: Path) -> str:
    """Use a repository-relative path when the artifact lives in this project."""

    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def run_model(
    model: str,
    dataset: list[dict[str, Any]],
    prompt: str,
    base_url: str,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    latencies: list[float] = []

    print(f"\nRunning {model} on {len(dataset)} examples...")
    for index, example in enumerate(dataset, start=1):
        try:
            output, latency, raw = generate_json(
                model=model,
                system_prompt=prompt,
                ticket=example["ticket"],
                base_url=base_url,
            )
        except OllamaError as exc:
            raise SystemExit(f"\n{exc}") from exc

        latencies.append(latency)
        records.append(
            {
                "id": example["id"],
                "ticket": example["ticket"],
                "expected": example["expected"],
                "output": output,
                "raw_output": raw,
                "slices": example.get("slices", []),
                "latency_seconds": latency,
            }
        )
        print(f"  [{index:>2}/{len(dataset)}] {example['id']} ({latency:.2f}s)")

    score = score_records(records)
    score["latency_seconds"] = {
        "mean": statistics.fmean(latencies),
        "median": statistics.median(latencies),
        "max": max(latencies),
    }
    return {
        "model": model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "score": score,
        "records": records,
    }


def print_summary(result: dict[str, Any]) -> None:
    metrics = result["score"]["metrics"]
    latency = result["score"]["latency_seconds"]
    print(f"\n{result['model']}")
    print("-" * len(result["model"]))
    for name, value in metrics.items():
        print(f"{name.replace('_', ' ').title():<28} {value:>7.1%}")
    print(f"{'Median latency':<28} {latency['median']:>6.2f}s")

    errors = result["score"].get("error_summary", {})
    if errors:
        ranked_errors = sorted(errors.items(), key=lambda item: (-item[1], item[0]))
        summary = ", ".join(
            f"{name.replace('_', ' ')}={count}" for name, count in ranked_errors
        )
        print(f"Top errors: {summary}")

    slices = result["score"].get("slices", {})
    if slices:
        weakest = sorted(
            slices.items(), key=lambda item: (item[1]["exact_match"], item[0])
        )[:3]
        summary = ", ".join(
            f"{name}={values['exact_match']:.0%} (n={values['count']})"
            for name, values in weakest
        )
        print(f"Weakest slices: {summary}")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser with development-safe defaults."""

    parser = argparse.ArgumentParser(
        description="Evaluate local Ollama models on support-ticket triage."
    )
    parser.add_argument("--models", nargs="+", required=True, help="Ollama model names")
    parser.add_argument(
        "--split",
        choices=["development", "test", "all"],
        default="development",
        help="Dataset split (default: development)",
    )
    parser.add_argument("--limit", type=int, help="Run only the first N selected examples")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dataset = load_dataset(args.dataset, args.split)
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit must be at least 1")
        dataset = dataset[: args.limit]

    prompt = args.prompt.read_text(encoding="utf-8")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for model in args.models:
        result = run_model(model, dataset, prompt, args.base_url)
        result["evaluation"] = {
            "split": args.split,
            "selected_examples": len(dataset),
            "dataset_path": portable_path(args.dataset),
            "dataset_sha256": file_sha256(args.dataset),
            "prompt_path": portable_path(args.prompt),
            "prompt_sha256": file_sha256(args.prompt),
            "temperature": 0,
        }
        output_path = args.output_dir / f"{model_slug(model)}-{args.split}-{timestamp}.json"
        output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print_summary(result)
        print(f"Full result: {output_path}")


if __name__ == "__main__":
    main()
