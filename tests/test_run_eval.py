"""Tests for portable evaluation metadata."""

from pathlib import Path
import unittest

from run_eval import DEFAULT_DATASET, portable_path


class PortablePathTests(unittest.TestCase):
    def test_makes_repository_path_relative(self):
        self.assertEqual(
            portable_path(DEFAULT_DATASET),
            "evals/support_triage/dataset.jsonl",
        )

    def test_preserves_external_path(self):
        path = Path("/tmp/external-eval.jsonl")
        self.assertEqual(portable_path(path), str(path))


if __name__ == "__main__":
    unittest.main()
