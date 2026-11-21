import json
import tempfile
import unittest
from pathlib import Path

from scripts.blind_edits import main


class BlindEditsTest(unittest.TestCase):
    def test_same_brief_produces_a_blind_ballot_and_private_record(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source = workspace / "input.json"
            source.write_text(json.dumps({
                "draft": "I counted 18 responses [1].",
                "assignment": "Describe the survey limits.",
                "goal": "Distinguish the sample from the population.",
                "tone": "Academic",
            }), encoding="utf-8")
            output = workspace / "run"
            calls: list[tuple[str, str]] = []
            candidates = ["I counted all 18 responses [1].", "I counted 18 responses [1]."]

            def edit(instruction: str, brief: str) -> str:
                calls.append((instruction, brief))
                return candidates[len(calls) - 1]

            main([str(source), str(output)], editor=edit)

            self.assertEqual(len(calls), 2)
            self.assertNotEqual(calls[0][0], calls[1][0])
            self.assertEqual(calls[0][1], calls[1][1])
            for value in json.loads(source.read_text(encoding="utf-8")).values():
                self.assertIn(value, calls[0][1])

            record = json.loads((output / "private.json").read_text(encoding="utf-8"))
            self.assertEqual(record["original_words"], 5)
            self.assertEqual(record["service_fee_usd"], 0)
            self.assertEqual(set(record["mapping"].values()), {"basic_copyedit", "balik"})
            for method, (instruction, _) in zip(("basic_copyedit", "balik"), calls):
                self.assertEqual(record["instructions"][method], instruction)
            self.assertIn("revision", record["model"])
            self.assertIn("max_tokens", record["settings"])
            self.assertGreaterEqual(record["elapsed_seconds"], 0)
            self.assertEqual(output.stat().st_mode & 0o777, 0o700)
            self.assertEqual((output / "private.json").stat().st_mode & 0o777, 0o600)

            ballot = (output / "ballot.md").read_text(encoding="utf-8")
            for label, method in record["mapping"].items():
                candidate = dict(zip(("basic_copyedit", "balik"), candidates))[method]
                self.assertIn(f"## Version {label}\n\n> {candidate}\n", ballot)
            self.assertIn("A, B, or Equally good", ballot)
            self.assertNotIn(record["model"]["id"], ballot)
            for secret in ("basic_copyedit", "balik", "detector", "mapping"):
                self.assertNotIn(secret, ballot.lower())
