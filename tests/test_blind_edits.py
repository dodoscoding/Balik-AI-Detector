import json
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from scripts.blind_edits import main


class BlindEditsTest(unittest.TestCase):
    def setUp(self):
        workspace = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.source = workspace / "input.json"
        self.output = workspace / "run"
        self.brief = {
            "draft": "I counted 18 responses [1].",
            "assignment": "Describe the survey limits.",
            "goal": "Distinguish the sample from the population.",
            "tone": "Academic",
        }
        self.source.write_text(json.dumps(self.brief), encoding="utf-8")
        self.args = [str(self.source), str(self.output)]

    def test_same_brief_produces_a_blind_ballot_and_private_record(self):
        calls: list[tuple[str, str]] = []
        candidates = {
            "basic_copyedit": "I counted all 18 responses [1].",
            "balik": "I counted 18 responses [1].",
        }
        edits = iter(candidates.values())

        def edit(instruction: str, brief: str) -> str:
            calls.append((instruction, brief))
            return next(edits)

        main(self.args, editor=edit)

        self.assertEqual(len(calls), 2)
        self.assertNotEqual(calls[0][0], calls[1][0])
        self.assertEqual(json.loads(calls[0][1]), self.brief)
        self.assertEqual(calls[0][1], calls[1][1])

        private_path = self.output / "private.json"
        record = json.loads(private_path.read_text(encoding="utf-8"))
        self.assertEqual(record["original_words"], 5)
        self.assertEqual(record["service_fee_usd"], 0)
        self.assertEqual(set(record["mapping"].values()), set(candidates))
        for method, (instruction, _) in zip(candidates, calls):
            self.assertEqual(record["instructions"][method], instruction)
        self.assertIn("revision", record["model"])
        self.assertIn("max_tokens", record["settings"])
        self.assertGreaterEqual(record["elapsed_seconds"], 0)
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        self.assertEqual(private_path.stat().st_mode & 0o777, 0o600)

        ballot = (self.output / "ballot.md").read_text(encoding="utf-8")
        for label, method in record["mapping"].items():
            self.assertIn(f"## Version {label}\n\n> {candidates[method]}\n", ballot)
        for value in self.brief.values():
            self.assertIn(value, ballot)
        self.assertIn("A, B, or Equally good", ballot)
        self.assertNotIn(record["model"]["id"], ballot)
        for secret in ("basic_copyedit", "balik", "detector", "mapping"):
            self.assertNotIn(secret, ballot.lower())

    def test_rejects_marked_passage_metadata_before_generation(self):
        self.brief["marked_passage"] = "I counted 18 responses [1]."
        self.source.write_text(json.dumps(self.brief), encoding="utf-8")

        def edit(instruction: str, brief: str) -> str:
            self.fail("A marked passage reached the editor")

        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as error:
            main(self.args, editor=edit)

        self.assertEqual(error.exception.code, 2)
        self.assertFalse(self.output.exists())

    def test_second_edit_failure_leaves_no_ballot_and_can_be_retried(self):
        candidates = iter(["I counted 18 responses [1].", ""])

        with self.assertRaisesRegex(ValueError, "empty draft"):
            main(self.args, editor=lambda _instruction, _brief: next(candidates))

        self.assertFalse(self.output.exists())
        main(self.args, editor=lambda _instruction, _brief: self.brief["draft"])
        self.assertTrue((self.output / "ballot.md").is_file())
