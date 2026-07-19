import tempfile
import unittest
from pathlib import Path

from open_product_evals.calibration import (
    DIMENSIONS,
    RUBRIC_VERSION,
    build_annotation_template,
    compare_annotations,
    quadratic_weighted_kappa,
    render_calibration_markdown,
    validate_annotations,
    validate_calibration_dataset,
    write_jsonl,
)


def annotation(record_id, reviewer, scores, critical_failure):
    return {
        "id": record_id,
        "reviewer": reviewer,
        "dataset_fingerprint": "a" * 64,
        "rubric_version": RUBRIC_VERSION,
        "scores": dict(zip(DIMENSIONS, scores)),
        "critical_failure": critical_failure,
        "notes": "",
    }


class CalibrationTests(unittest.TestCase):
    def test_builds_blank_annotation_template_without_gold_labels(self):
        dataset = [
            {
                "id": "rq-cal-001",
                "split": "calibration",
                "ticket": "A fictional ticket",
                "draft_response": "A fictional response",
                "slices": ["example"],
            }
        ]
        template = build_annotation_template(dataset, "reviewer-a")
        self.assertEqual(template[0]["reviewer"], "reviewer-a")
        self.assertEqual(len(template[0]["dataset_fingerprint"]), 64)
        self.assertEqual(template[0]["rubric_version"], RUBRIC_VERSION)
        self.assertEqual(template[0]["scores"], {dimension: None for dimension in DIMENSIONS})
        self.assertIsNone(template[0]["critical_failure"])

    def test_dataset_rejects_embedded_gold_labels(self):
        dataset = [
            {
                "id": "rq-cal-001",
                "split": "calibration",
                "ticket": "A fictional ticket",
                "draft_response": "A fictional response",
                "slices": ["example"],
                "critical_failure": True,
            }
        ]
        with self.assertRaisesRegex(ValueError, "must not contain labels"):
            validate_calibration_dataset(dataset)

    def test_annotation_validation_rejects_incomplete_review(self):
        incomplete = annotation("rq-cal-001", "reviewer-a", [4, 4, 4, 4], False)
        incomplete["scores"]["communication"] = None
        with self.assertRaisesRegex(ValueError, "communication must be an integer"):
            validate_annotations([incomplete])

    def test_quadratic_weighted_kappa_is_one_for_exact_agreement(self):
        self.assertEqual(quadratic_weighted_kappa([1, 2, 3, 4], [1, 2, 3, 4]), 1.0)

    def test_quadratic_weighted_kappa_is_undefined_without_score_variation(self):
        self.assertIsNone(quadratic_weighted_kappa([4, 4, 4], [4, 4, 4]))

    def test_compares_scores_and_ranks_critical_disagreement_first(self):
        reviewer_a = [
            annotation("rq-cal-001", "reviewer-a", [4, 4, 4, 4], False),
            annotation("rq-cal-002", "reviewer-a", [1, 1, 2, 2], True),
            annotation("rq-cal-003", "reviewer-a", [2, 2, 3, 3], False),
            annotation("rq-cal-004", "reviewer-a", [3, 3, 4, 4], False),
        ]
        reviewer_b = [
            annotation("rq-cal-001", "reviewer-b", [4, 4, 4, 4], False),
            annotation("rq-cal-002", "reviewer-b", [1, 2, 2, 2], False),
            annotation("rq-cal-003", "reviewer-b", [2, 2, 3, 4], False),
            annotation("rq-cal-004", "reviewer-b", [3, 3, 4, 4], False),
        ]
        comparison = compare_annotations(reviewer_a, reviewer_b)
        self.assertEqual(comparison["example_count"], 4)
        self.assertEqual(comparison["disagreements"][0]["id"], "rq-cal-002")
        self.assertTrue(comparison["disagreements"][0]["critical_mismatch"])
        self.assertAlmostEqual(
            comparison["dimensions"]["communication"]["exact_agreement"], 0.75
        )
        self.assertEqual(
            comparison["dimensions"]["correctness"]["reviewer_a_distribution"],
            {1: 1, 2: 1, 3: 1, 4: 1},
        )
        self.assertAlmostEqual(
            comparison["critical_failure"]["exact_agreement"], 0.75
        )
        self.assertFalse(comparison["calibration_gate_passed"])

        report = render_calibration_markdown(comparison)
        self.assertIn("human-human agreement", report)
        self.assertIn("`rq-cal-002`", report)
        self.assertIn("calibration gate: **FAIL**", report)
        self.assertIn("Score distributions", report)
        self.assertIn("1/1/1/1", report)

    def test_all_negative_critical_labels_cannot_pass_coverage_gate(self):
        reviewer_a = [
            annotation("rq-cal-001", "reviewer-a", [1, 2, 3, 4], False),
            annotation("rq-cal-002", "reviewer-a", [2, 3, 4, 1], False),
            annotation("rq-cal-003", "reviewer-a", [3, 4, 1, 2], False),
            annotation("rq-cal-004", "reviewer-a", [4, 1, 2, 3], False),
        ]
        reviewer_b = [
            annotation("rq-cal-001", "reviewer-b", [1, 2, 3, 4], False),
            annotation("rq-cal-002", "reviewer-b", [2, 3, 4, 1], False),
            annotation("rq-cal-003", "reviewer-b", [3, 4, 1, 2], False),
            annotation("rq-cal-004", "reviewer-b", [4, 1, 2, 3], False),
        ]
        comparison = compare_annotations(reviewer_a, reviewer_b)
        self.assertEqual(comparison["critical_failure"]["exact_agreement"], 1.0)
        self.assertFalse(comparison["critical_failure"]["coverage_gate_passed"])
        self.assertFalse(comparison["calibration_gate_passed"])

    def test_all_positive_critical_labels_cannot_pass_coverage_gate(self):
        reviewer_a = [
            annotation("rq-cal-001", "reviewer-a", [1, 2, 3, 4], True),
            annotation("rq-cal-002", "reviewer-a", [2, 3, 4, 1], True),
            annotation("rq-cal-003", "reviewer-a", [3, 4, 1, 2], True),
            annotation("rq-cal-004", "reviewer-a", [4, 1, 2, 3], True),
        ]
        reviewer_b = [
            annotation("rq-cal-001", "reviewer-b", [1, 2, 3, 4], True),
            annotation("rq-cal-002", "reviewer-b", [2, 3, 4, 1], True),
            annotation("rq-cal-003", "reviewer-b", [3, 4, 1, 2], True),
            annotation("rq-cal-004", "reviewer-b", [4, 1, 2, 3], True),
        ]
        comparison = compare_annotations(reviewer_a, reviewer_b)
        self.assertEqual(comparison["critical_failure"]["exact_agreement"], 1.0)
        self.assertFalse(comparison["critical_failure"]["coverage_gate_passed"])
        self.assertFalse(comparison["calibration_gate_passed"])

    def test_rejects_different_id_sets(self):
        reviewer_a = [annotation("rq-cal-001", "reviewer-a", [4, 4, 4, 4], False)]
        reviewer_b = [annotation("rq-cal-002", "reviewer-b", [4, 4, 4, 4], False)]
        with self.assertRaisesRegex(ValueError, "annotation id sets differ"):
            compare_annotations(reviewer_a, reviewer_b)

    def test_rejects_different_dataset_fingerprints(self):
        reviewer_a = [annotation("rq-cal-001", "reviewer-a", [4, 4, 4, 4], False)]
        reviewer_b = [annotation("rq-cal-001", "reviewer-b", [4, 4, 4, 4], False)]
        reviewer_b[0]["dataset_fingerprint"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "dataset fingerprints differ"):
            compare_annotations(reviewer_a, reviewer_b)

    def test_rejects_different_rubric_versions(self):
        reviewer_a = [annotation("rq-cal-001", "reviewer-a", [4, 4, 4, 4], False)]
        reviewer_b = [annotation("rq-cal-001", "reviewer-b", [4, 4, 4, 4], False)]
        reviewer_b[0]["rubric_version"] = "different-version"
        with self.assertRaisesRegex(ValueError, "rubric versions differ"):
            compare_annotations(reviewer_a, reviewer_b)

    def test_write_jsonl_refuses_to_replace_existing_review(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            output = Path(temp_directory) / "review.jsonl"
            records = [annotation("rq-cal-001", "reviewer-a", [4, 4, 4, 4], False)]
            write_jsonl(records, output)
            with self.assertRaises(FileExistsError):
                write_jsonl(records, output)
