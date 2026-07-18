import unittest

from open_product_evals.scoring import normalize_output, score_records


class NormalizeOutputTests(unittest.TestCase):
    def test_normalizes_strings(self):
        self.assertEqual(
            normalize_output(
                {"category": " Billing ", "priority": "HIGH", "escalate": True}
            ),
            {"category": "billing", "priority": "high", "escalate": True},
        )

    def test_rejects_invalid_schema(self):
        self.assertIsNone(
            normalize_output(
                {"category": "sales", "priority": "high", "escalate": False}
            )
        )
        self.assertIsNone(
            normalize_output(
                {"category": "billing", "priority": "high", "escalate": "yes"}
            )
        )


class ScoreRecordsTests(unittest.TestCase):
    def test_scores_exact_and_partial_matches(self):
        records = [
            {
                "id": "one",
                "expected": {
                    "category": "billing",
                    "priority": "high",
                    "escalate": True,
                },
                "output": {
                    "category": "billing",
                    "priority": "high",
                    "escalate": True,
                },
                "slices": ["billing"],
            },
            {
                "id": "two",
                "expected": {
                    "category": "feature_request",
                    "priority": "low",
                    "escalate": False,
                },
                "output": {
                    "category": "feature_request",
                    "priority": "medium",
                    "escalate": False,
                },
                "slices": ["feature"],
            },
        ]

        result = score_records(records)
        self.assertEqual(result["metrics"]["category_accuracy"], 1.0)
        self.assertEqual(result["metrics"]["priority_accuracy"], 0.5)
        self.assertEqual(result["metrics"]["exact_match"], 0.5)
        self.assertEqual(result["metrics"]["escalation_recall"], 1.0)

    def test_invalid_output_counts_as_missed_escalation(self):
        result = score_records(
            [
                {
                    "id": "one",
                    "expected": {
                        "category": "account_access",
                        "priority": "urgent",
                        "escalate": True,
                    },
                    "output": None,
                }
            ]
        )
        self.assertEqual(result["metrics"]["valid_schema_rate"], 0.0)
        self.assertEqual(result["metrics"]["escalation_recall"], 0.0)


if __name__ == "__main__":
    unittest.main()

