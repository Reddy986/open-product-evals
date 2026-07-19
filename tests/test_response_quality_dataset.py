import json
import unittest
from pathlib import Path

from open_product_evals.calibration import validate_calibration_dataset


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evals" / "response_quality" / "dataset.jsonl"


class ResponseQualityDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = [
            json.loads(line)
            for line in DATASET.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_has_twelve_unlabeled_calibration_examples(self):
        records = validate_calibration_dataset(self.records)
        self.assertEqual(len(records), 12)
        self.assertEqual(len({record["id"] for record in records}), 12)
        self.assertTrue(all(record["split"] == "calibration" for record in records))

    def test_covers_high_risk_and_quality_slices(self):
        slices = {slice_name for record in self.records for slice_name in record["slices"]}
        self.assertTrue(
            {
                "critical_failure_candidate",
                "credential_request",
                "fabricated_action",
                "multi_intent",
                "well_qualified",
            }.issubset(slices)
        )
