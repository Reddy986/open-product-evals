import unittest

from open_product_evals.reporting import comparison_markdown, evaluate_gate


def sample_result(**metric_overrides):
    metrics = {
        "valid_schema_rate": 1.0,
        "escalation_recall": 0.95,
        "exact_match": 0.75,
    }
    metrics.update(metric_overrides)
    return {
        "model": "example-model",
        "score": {
            "count": 20,
            "metrics": metrics,
            "latency_seconds": {"median": 1.25},
            "error_summary": {"wrong_priority": 3, "wrong_category": 1},
        },
    }


class ReportingTests(unittest.TestCase):
    def test_gate_passes_at_or_above_thresholds(self):
        self.assertTrue(evaluate_gate(sample_result())["passed"])

    def test_gate_identifies_miss(self):
        gate = evaluate_gate(sample_result(escalation_recall=0.5))
        self.assertFalse(gate["passed"])
        self.assertFalse(gate["checks"]["escalation_recall"]["passed"])

    def test_markdown_contains_decision_context(self):
        report = comparison_markdown([sample_result(exact_match=0.5)])
        self.assertIn("| example-model | 20 | 100.0% | 95.0% | 50.0%", report)
        self.assertIn("| FAIL |", report)
        self.assertIn("wrong priority (3)", report)
        self.assertIn("not a production-safety certification", report)

    def test_rejects_incomparable_runs(self):
        first = sample_result()
        first["evaluation"] = {
            "dataset_sha256": "abc",
            "split": "test",
            "selected_examples": 20,
        }
        second = sample_result()
        second["evaluation"] = {
            "dataset_sha256": "def",
            "split": "test",
            "selected_examples": 20,
        }
        with self.assertRaisesRegex(ValueError, "different dataset fingerprints"):
            comparison_markdown([first, second])


if __name__ == "__main__":
    unittest.main()
