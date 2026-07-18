import unittest

from open_product_evals.baseline import predict


class BaselineTests(unittest.TestCase):
    def test_billing_risk(self):
        self.assertEqual(
            predict("Refund this unauthorized charge."),
            {"category": "billing", "priority": "urgent", "escalate": True},
        )

    def test_feature_request(self):
        self.assertEqual(
            predict("Please add a dark mode."),
            {
                "category": "feature_request",
                "priority": "medium",
                "escalate": False,
            },
        )

    def test_general_question(self):
        self.assertEqual(
            predict("Where can I read your privacy policy?"),
            {
                "category": "general_question",
                "priority": "low",
                "escalate": False,
            },
        )


if __name__ == "__main__":
    unittest.main()

