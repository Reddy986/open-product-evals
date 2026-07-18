import json
import unittest
from collections import Counter
from pathlib import Path

from open_product_evals.scoring import normalize_output


DATASET = (
    Path(__file__).resolve().parents[1]
    / "evals"
    / "support_triage"
    / "dataset.jsonl"
)


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [json.loads(line) for line in DATASET.read_text().splitlines() if line]

    def test_has_expected_size_and_splits(self):
        self.assertEqual(len(self.rows), 60)
        self.assertEqual(Counter(row["split"] for row in self.rows), {"development": 40, "test": 20})

    def test_ids_are_unique(self):
        ids = [row["id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_expected_labels_are_valid(self):
        for row in self.rows:
            self.assertIsNotNone(normalize_output(row["expected"]), row["id"])
            self.assertTrue(row["ticket"].strip(), row["id"])
            self.assertTrue(row["slices"], row["id"])


if __name__ == "__main__":
    unittest.main()

