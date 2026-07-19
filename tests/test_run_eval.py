"""Tests for portable evaluation metadata."""

from pathlib import Path
import unittest

from run_eval import DEFAULT_DATASET, build_parser, portable_path


class PortablePathTests(unittest.TestCase):
    def test_makes_repository_path_relative(self):
        self.assertEqual(
            portable_path(DEFAULT_DATASET),
            "evals/support_triage/dataset.jsonl",
        )

    def test_preserves_external_path(self):
        path = Path("/tmp/external-eval.jsonl")
        self.assertEqual(portable_path(path), str(path))


class ParserDefaultsTests(unittest.TestCase):
    def test_defaults_to_development_split(self):
        args = build_parser().parse_args(["--models", "qwen3:4b"])
        self.assertEqual(args.split, "development")


if __name__ == "__main__":
    unittest.main()
