import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(__file__).resolve().parents[1] / "scripts" / "check_m1_split.py"


def make_register(final_count=3):
    register = {}
    for group, prefix, count in (("rehearsal", "R", 4), ("final", "F", final_count)):
        register[group] = [
            {
                "author": f"W-{prefix}{number}",
                "draft": f"D-{prefix}{number}",
                "related": [f"P-{prefix}{number}"],
                "peer_permission": True,
                "cloud_permission": "not_requested",
            }
            for number in range(count)
        ]
    return register


class CheckM1SplitTests(unittest.TestCase):
    def run_checker(self, raw_register):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "register.json"
            path.write_text(raw_register, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.stderr, "")
        return result.returncode, json.loads(result.stdout)

    def test_rejects_duplicate_final_group(self):
        register = make_register()
        overlapping_final = make_register()["final"]
        overlapping_final[0]["author"] = register["rehearsal"][0]["author"]
        raw_register = (
            '{"final": ' + json.dumps(overlapping_final) + ", " + json.dumps(register)[1:]
        )

        exit_code, report = self.run_checker(raw_register)

        self.assertEqual(exit_code, 1)
        self.assertEqual(report, {"result": "failed", "errors": {"unreadable_register": 1}})

    def test_rejects_duplicate_permission_key(self):
        raw_register = json.dumps(make_register()).replace(
            '"peer_permission": true',
            '"peer_permission": false, "peer_permission": true',
            1,
        )

        exit_code, report = self.run_checker(raw_register)

        self.assertEqual(exit_code, 1)
        self.assertEqual(report, {"result": "failed", "errors": {"unreadable_register": 1}})

    def test_counts_duplicate_source_once_in_each_group(self):
        register = make_register()
        for drafts in register.values():
            drafts[1]["draft"] = drafts[0]["draft"]

        exit_code, report = self.run_checker(json.dumps(register))

        self.assertEqual(exit_code, 1)
        self.assertEqual(report["result"], "failed")
        self.assertEqual(report["errors"], {"reused_artifact_code": 2})
        self.assertEqual(
            report["counts"],
            {"rehearsal": {"authors": 4, "drafts": 3}, "final": {"authors": 3, "drafts": 2}},
        )

    def test_accepts_valid_splits_with_either_final_group_size(self):
        for final_count in (3, 4):
            with self.subTest(final_count=final_count):
                exit_code, report = self.run_checker(json.dumps(make_register(final_count)))

                self.assertEqual(exit_code, 0)
                self.assertEqual(
                    report,
                    {
                        "result": "passed",
                        "counts": {
                            "rehearsal": {"authors": 4, "drafts": 4},
                            "final": {"authors": final_count, "drafts": final_count},
                        },
                        "errors": {},
                    },
                )
