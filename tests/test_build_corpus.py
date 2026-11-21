import contextlib
import csv
import hashlib
import gzip
import io
import json
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import unittest.mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_corpus  # noqa: E402
import corpus_sources  # noqa: E402

INTRO = "\n\n".join("Sentence " + "word " * 100 for _ in range(4))


def pile_line(number, license_text="https://creativecommons.org/licenses/by/4.0/"):
    return json.dumps(
        {
            "id": f"0705.{number:04d}",
            "text": f"# T\n\n## 1 Introduction\n\n{INTRO}\n\n## 2 End\n\nx",
            "created": "2007-05-08T00:00:00",
            "metadata": {"license": license_text, "authors": f"Writer {number}, Shared Person"},
        }
    )


def oai_xml(license_url, updated="2008-01-01"):
    return (
        '<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><GetRecord><record><metadata>'
        '<arXiv xmlns="http://arxiv.org/OAI/arXiv/"><created>2007-05-08</created>'
        f"<updated>{updated}</updated><license>{license_url}</license></arXiv>"
        "</metadata></record></GetRecord></OAI-PMH>"
    )


class BuildTests(unittest.TestCase):
    def test_end_to_end_with_fixtures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "p.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle, ["essay_id_comp", "competition_set", "full_text", "prompt_name", "grade_level"]
                )
                writer.writeheader()
                for prompt in ("Alpha topic", "Beta topic", "Gamma topic"):
                    for n in range(6):
                        for _ in range(2):  # long format: repeated rows per essay
                            writer.writerow(
                                {
                                    "essay_id_comp": f"{prompt[:2]}{n:04d}".upper(),
                                    "competition_set": "train",
                                    "full_text": f"{prompt} essay {n}",
                                    "prompt_name": prompt,
                                    "grade_level": "9",
                                }
                            )
            shard = root / "s.jsonl.gz"
            lines = [pile_line(n) for n in range(10)] + [pile_line(50, "https://creativecommons.org/licenses/by-sa/4.0/")]
            shard.write_bytes(gzip.compress("\n".join(lines).encode()))

            def fetch(arxiv_id):
                if arxiv_id.endswith("0003"):
                    return oai_xml("http://arxiv.org/licenses/nonexclusive-distrib/1.0/")
                return oai_xml("http://creativecommons.org/licenses/by/4.0/")

            manifest = root / "manifest.jsonl"
            split_file = root / "split.json"
            data_dir = root / "data"
            report = build_corpus.build(
                persuade_csv=csv_path,
                arxiv_shards=[shard],
                data_dir=data_dir,
                manifest_path=manifest,
                split_path=split_file,
                per_prompt=4,
                arxiv_count=9,
                test_fraction=0.3,
                seed=1,
                today="2026-11-21",
                fetch_oai=fetch,
            )
            rows = [json.loads(line) for line in manifest.read_text().splitlines()]
            self.assertEqual(report["persuade"], 12)
            self.assertEqual(report["arxiv"], 9)
            self.assertEqual(report["arxiv_rejected"].get("oai_rejected"), 1)
            self.assertNotIn("candidates_found", report["arxiv_rejected"])
            self.assertEqual(report["arxiv_candidates"], 10)  # the share-alike paper is not a candidate
            test_ids = sorted(r["id"] for r in rows if r["split"] == "test")
            self.assertEqual(
                json.loads(split_file.read_text())["test_ids_sha256"],
                hashlib.sha256("\n".join(test_ids).encode()).hexdigest(),
            )
            self.assertEqual([r["id"] for r in rows], sorted(r["id"] for r in rows))
            for row in rows:
                text = (data_dir / row["path"]).read_text(encoding="utf-8")
                self.assertEqual(corpus_sources.sha256_text(text), row["sha256"])
                self.assertIn(row["split"], ("dev", "test"))
            self.assertEqual(json.loads(split_file.read_text())["test_split_date"], "2026-11-21")
            checker = ROOT / "scripts" / "check_manifest.py"
            if checker.exists():
                result = subprocess.run(
                    [sys.executable, str(checker), str(manifest), "--data-dir", str(data_dir)],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class SplitPinTests(unittest.TestCase):
    def write_csv(self, path, prompts):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, ["essay_id_comp", "full_text", "prompt_name"])
            writer.writeheader()
            for prompt in prompts:
                for n in range(8):
                    writer.writerow(
                        {"essay_id_comp": f"{prompt[-1]}{n}".upper(), "full_text": f"{prompt} {n}",
                         "prompt_name": prompt}
                    )

    def build(self, root, **over):
        args = dict(
            persuade_csv=root / "p.csv", arxiv_shards=[], data_dir=root / "data",
            manifest_path=root / "manifest.jsonl", split_path=root / "split.json",
            per_prompt=8, arxiv_count=0, test_fraction=0.3, seed=1, today="2026-11-21",
            fetch_oai=None,
        )
        args.update(over)
        return build_corpus.build(**args)

    def test_rebuild_with_other_test_ids_fails_and_keeps_the_old_split(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(root / "p.csv", [f"Prompt{c}" for c in "ABCDEFGH"])
            self.build(root)
            before = (root / "split.json").read_text()
            with self.assertRaises(build_corpus.SplitChangedError):
                self.build(root, test_fraction=0.7, today="2027-01-01")
            self.assertEqual((root / "split.json").read_text(), before)

    def test_rebuild_with_same_test_ids_keeps_the_date(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(root / "p.csv", ["PromptA", "PromptB", "PromptC", "PromptD"])
            self.build(root)
            self.build(root, today="2027-01-01")
            self.assertEqual(json.loads((root / "split.json").read_text())["test_split_date"], "2026-11-21")

    def test_cli_exits_non_zero_with_a_message_when_the_test_set_changed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(root / "p.csv", [f"Prompt{c}" for c in "ABCDEFGH"])
            argv = ["build_corpus.py", "--persuade-csv", str(root / "p.csv"),
                    "--data-dir", str(root / "data"), "--corpus-dir", str(root / "corpus"),
                    "--per-prompt", "8"]
            with unittest.mock.patch.object(sys, "argv", argv + ["--test-fraction", "0.3"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(build_corpus.main(), 0)
            err = io.StringIO()
            with unittest.mock.patch.object(sys, "argv", argv + ["--test-fraction", "0.7"]), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                self.assertEqual(build_corpus.main(), 1)
            self.assertIn("test set", err.getvalue())


if __name__ == "__main__":
    unittest.main()
