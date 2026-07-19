"""Guard the one-variable priority-rubric experiment."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROMPT_V1 = ROOT / "evals" / "support_triage" / "prompt.txt"
PROMPT_V2 = ROOT / "evals" / "support_triage" / "prompt_v2.txt"


def prompt_sections(text: str) -> tuple[str, str, str]:
    prefix, remainder = text.split("Priority rules:", maxsplit=1)
    priority, suffix = remainder.split("Escalate when", maxsplit=1)
    return prefix, priority, suffix


class PromptExperimentTests(unittest.TestCase):
    def test_only_priority_section_changes(self):
        v1 = prompt_sections(PROMPT_V1.read_text(encoding="utf-8"))
        v2 = prompt_sections(PROMPT_V2.read_text(encoding="utf-8"))

        self.assertEqual(v1[0], v2[0])
        self.assertNotEqual(v1[1], v2[1])
        self.assertEqual(v1[2].rstrip(), v2[2].rstrip())

    def test_priority_and_escalation_are_explicitly_separate(self):
        prompt = PROMPT_V2.read_text(encoding="utf-8")
        self.assertIn("Priority and escalation\nare separate decisions", prompt)
        self.assertIn("needing a human does not automatically", prompt)


if __name__ == "__main__":
    unittest.main()
