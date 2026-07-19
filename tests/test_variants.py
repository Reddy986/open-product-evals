"""Tests for strict paired prompt-variant analysis."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from open_product_evals.variants import (
    paired_variant_analysis,
    paired_variant_markdown,
)


def sample_pair():
    expected = [
        {"category": "billing", "priority": "high", "escalate": True},
        {"category": "technical_issue", "priority": "medium", "escalate": False},
        {"category": "feature_request", "priority": "low", "escalate": False},
        {"category": "account_access", "priority": "high", "escalate": True},
    ]
    baseline_outputs = [
        expected[0],
        {"category": "technical_issue", "priority": "high", "escalate": False},
        expected[2],
        {"category": "account_access", "priority": "high", "escalate": False},
    ]
    candidate_outputs = [
        {"category": "general_question", "priority": "high", "escalate": True},
        expected[1],
        None,
        expected[3],
    ]

    def result(prompt_sha, outputs, metrics, latency):
        return {
            "model": "example-model",
            "evaluation": {
                "dataset_sha256": "dataset-sha",
                "split": "development",
                "selected_examples": 4,
                "prompt_sha256": prompt_sha,
                "temperature": 0,
            },
            "score": {
                "count": 4,
                "metrics": metrics,
                "latency_seconds": latency,
            },
            "records": [
                {
                    "id": f"dev-{index:03d}",
                    "expected": expected[index - 1],
                    "output": outputs[index - 1],
                }
                for index in range(1, 5)
            ],
        }

    baseline = result(
        "prompt-v1",
        baseline_outputs,
        {
            "category_accuracy": 1.0,
            "priority_accuracy": 0.75,
            "escalation_accuracy": 0.75,
            "exact_match": 0.5,
            "valid_schema_rate": 1.0,
            "escalation_precision": 1.0,
            "escalation_recall": 0.5,
        },
        {"mean": 2.0, "median": 1.5, "max": 4.0},
    )
    candidate = result(
        "prompt-v2",
        candidate_outputs,
        {
            "category_accuracy": 0.5,
            "priority_accuracy": 0.75,
            "escalation_accuracy": 1.0,
            "exact_match": 0.5,
            "valid_schema_rate": 0.75,
            "escalation_precision": 1.0,
            "escalation_recall": 1.0,
        },
        {"mean": 2.5, "median": 2.0, "max": 5.0},
    )
    return baseline, candidate


class VariantAnalysisTests(unittest.TestCase):
    def test_reports_paired_transitions(self):
        baseline, candidate = sample_pair()
        analysis = paired_variant_analysis(baseline, candidate)

        self.assertEqual(analysis["transitions"]["exact"], {"improved": 2, "regressed": 2})
        self.assertEqual(
            analysis["transitions"]["fields"]["category"],
            {"improved": 0, "regressed": 2},
        )
        self.assertEqual(
            analysis["transitions"]["fields"]["priority"],
            {"improved": 1, "regressed": 1},
        )
        self.assertEqual(
            analysis["transitions"]["fields"]["escalate"],
            {"improved": 1, "regressed": 1},
        )
        self.assertEqual(analysis["identifiers"]["became_invalid"], ["dev-003"])

    def test_markdown_contains_fingerprints_deltas_ids_and_warning(self):
        baseline, candidate = sample_pair()
        report = paired_variant_markdown(
            baseline, candidate, baseline_label="Prompt v1", candidate_label="Prompt v2"
        )

        self.assertIn("Prompt v1 prompt SHA-256:** `prompt-v1`", report)
        self.assertIn("| Category Accuracy | 100.0% | 50.0% | -50.0 pp |", report)
        self.assertIn("| Median | 1.50s | 2.00s | +0.50s |", report)
        self.assertIn("**Exact regressions:** `dev-001`, `dev-003`", report)
        self.assertIn("does not establish generalization", report)

    def assert_incompatible(self, field, value, message):
        baseline, candidate = sample_pair()
        if field == "model":
            candidate[field] = value
        else:
            candidate["evaluation"][field] = value
        with self.assertRaisesRegex(ValueError, message):
            paired_variant_analysis(baseline, candidate)

    def test_rejects_different_models(self):
        self.assert_incompatible("model", "other-model", "model names differ")

    def test_rejects_different_dataset_fingerprints(self):
        self.assert_incompatible(
            "dataset_sha256", "other-dataset", "dataset fingerprints differ"
        )

    def test_rejects_different_splits(self):
        self.assert_incompatible("split", "test", "splits differ")

    def test_rejects_different_selected_example_counts(self):
        self.assert_incompatible(
            "selected_examples", 5, "selected-example counts differ"
        )

    def test_rejects_different_temperatures(self):
        self.assert_incompatible("temperature", 0.5, "temperatures differ")

    def test_rejects_different_record_ids(self):
        baseline, candidate = sample_pair()
        candidate["records"][0]["id"] = "other-id"
        with self.assertRaisesRegex(ValueError, "record ID sets differ"):
            paired_variant_analysis(baseline, candidate)

    def test_rejects_different_expected_labels(self):
        baseline, candidate = sample_pair()
        candidate["records"][0]["expected"] = {
            "category": "billing",
            "priority": "low",
            "escalate": True,
        }
        with self.assertRaisesRegex(ValueError, "expected labels differ"):
            paired_variant_analysis(baseline, candidate)

    def test_rejects_metric_set_changes(self):
        baseline, candidate = sample_pair()
        del candidate["score"]["metrics"]["exact_match"]
        with self.assertRaisesRegex(ValueError, "metric sets differ"):
            paired_variant_analysis(baseline, candidate)

    def test_does_not_mutate_inputs(self):
        baseline, candidate = sample_pair()
        baseline_copy = deepcopy(baseline)
        candidate_copy = deepcopy(candidate)
        paired_variant_analysis(baseline, candidate)
        self.assertEqual(baseline, baseline_copy)
        self.assertEqual(candidate, candidate_copy)

    def test_reproduces_published_prompt_experiment(self):
        root = Path(__file__).resolve().parents[1]
        baseline_dir = root / "results/published/2026-07-18-open-model-comparison"
        candidate_dir = root / "results/published/2026-07-18-priority-rubric-v2"

        expected = {
            "gemma3-4b-development.json": {
                "exact": {"improved": 2, "regressed": 10},
                "priority": {"improved": 3, "regressed": 7},
                "escalate": {"improved": 2, "regressed": 7},
                "became_invalid": [],
            },
            "qwen3-4b-development.json": {
                "exact": {"improved": 7, "regressed": 9},
                "priority": {"improved": 6, "regressed": 7},
                "escalate": {"improved": 1, "regressed": 3},
                "became_invalid": ["dev-015"],
            },
        }

        for filename, transitions in expected.items():
            with self.subTest(filename=filename):
                baseline = json.loads((baseline_dir / filename).read_text())
                candidate = json.loads((candidate_dir / filename).read_text())
                analysis = paired_variant_analysis(baseline, candidate)
                self.assertEqual(
                    analysis["transitions"]["exact"], transitions["exact"]
                )
                self.assertEqual(
                    analysis["transitions"]["fields"]["priority"],
                    transitions["priority"],
                )
                self.assertEqual(
                    analysis["transitions"]["fields"]["escalate"],
                    transitions["escalate"],
                )
                self.assertEqual(
                    analysis["identifiers"]["became_invalid"],
                    transitions["became_invalid"],
                )


if __name__ == "__main__":
    unittest.main()
