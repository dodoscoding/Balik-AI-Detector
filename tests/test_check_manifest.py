import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(__file__).resolve().parents[1] / "scripts" / "check_manifest.py"
spec = importlib.util.spec_from_file_location("check_manifest", CHECKER)
check_manifest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_manifest)
check = check_manifest.check

SPLIT = {"test_split_date": "2026-01-15", "method": "by prompt and author"}


def pinned(records, **over):
    """Split metadata whose hash matches the test ids of `records`."""
    ids = sorted(r["id"] for r in records if isinstance(r, dict) and r.get("split") == "test")
    meta = {**SPLIT, "test_ids_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest()}
    meta.update(over)
    return meta


def human(n=1, **over):
    record = {
        "id": f"H-{n}",
        "source": "persuade-2.0",
        "source_ref": f"ref{n}",
        "license": "CC-BY-4.0",
        "use": "product",
        "date": "2021-05-01",
        "source_type": "human",
        "register": "school_student",
        "population": "US students, grades 6-12",
        "language": "en",
        "writing_context": "academic",
        "authors": [f"A-{n}"],
        "prompt": f"P-{n}",
        "split": "dev",
        "path": f"persuade/H-{n}.txt",
        "sha256": "a" * 64,
        "derived_from": None,
    }
    record.update(over)
    return record


def ai(n=2, parent="H-1", **over):
    base = {
        "id": f"AI-{n}", "source_type": "ai", "authors": [], "date": "2024-03-01",
        "derived_from": parent, "path": f"ai/AI-{n}.txt",
    }
    base.update(over)
    return human(n, **base)


class CheckTests(unittest.TestCase):
    def codes(self, records, split="pinned"):
        if split == "pinned":
            split = pinned(records)
        counts, errors = check(records, split)
        return dict(errors)

    def test_valid_manifest_passes_and_counts_by_split_and_source_type(self):
        records = [human(1), ai(2), human(3, split="test")]
        counts, errors = check(records, pinned(records))
        self.assertEqual(errors, {})
        self.assertEqual(counts, {"dev": {"human": 1, "ai": 1}, "test": {"human": 1}})

    def test_empty_manifest_passes_with_zero_counts(self):
        counts, errors = check([], pinned([]))
        self.assertEqual((counts, dict(errors)), ({"dev": {}, "test": {}}, {}))

    def test_rejects_missing_or_extra_keys(self):
        missing = human(1)
        del missing["prompt"]
        self.assertEqual(self.codes([missing]), {"invalid_record": 1})
        self.assertEqual(self.codes([human(1, extra="x")]), {"invalid_record": 1})
        self.assertEqual(self.codes(["not an object"]), {"invalid_record": 1})

    def test_rejects_invalid_field_values(self):
        for field, value in (
            ("register", "adult"), ("language", "tr"), ("writing_context", "news"),
            ("split", "val"), ("source_type", "robot"), ("source_ref", ""),
            ("population", " "), ("id", "lowercase"), ("prompt", "p"),
            ("sha256", "A" * 64), ("sha256", "a" * 63), ("date", "2021-5-1"),
            ("authors", "A-1"), ("authors", ["bad"]), ("use", "both"),
        ):
            with self.subTest(field=field, value=value):
                self.assertEqual(self.codes([human(1, **{field: value})]), {"invalid_record": 1})

    def test_rejects_unknown_source(self):
        self.assertEqual(self.codes([human(1, source="kaggle")]), {"unknown_source": 1})

    def test_pes2o_is_not_a_source(self):
        self.assertEqual(self.codes([human(1, source="pes2o")]), {"unknown_source": 1})

    def test_rejects_unknown_license(self):
        self.assertEqual(self.codes([human(1, license="MIT")]), {"unknown_license": 1})

    def test_use_must_match_what_the_license_implies(self):
        self.assertEqual(self.codes([human(1, use="internal")]), {"wrong_use": 1})
        nc = human(1, license="CC-BY-NC-4.0", use="product")
        self.assertEqual(self.codes([nc]), {"wrong_use": 1})
        self.assertEqual(self.codes([human(1, license="CC-BY-NC-4.0", use="internal")]), {})

    def test_human_must_be_dated_strictly_before_the_cutoff(self):
        self.assertEqual(self.codes([human(1, date="2022-11-29")]), {})
        self.assertEqual(self.codes([human(1, date="2022-11-30")]), {"human_after_cutoff": 1})
        self.assertEqual(self.codes([human(1, date="2024-01-01")]), {"human_after_cutoff": 1})

    def test_human_without_a_date_is_rejected(self):
        self.assertEqual(self.codes([human(1, date=None)]), {"human_without_date": 1})

    def test_null_date_is_only_allowed_for_unknown(self):
        unknown = human(1, source_type="unknown", date=None)
        self.assertEqual(self.codes([unknown]), {})
        self.assertEqual(self.codes([ai(2, parent="H-1", date=None), human(1)]), {"invalid_record": 1})

    def test_author_list_depends_on_source_type(self):
        self.assertEqual(self.codes([human(1, authors=[])]), {"missing_authors": 1})
        self.assertEqual(self.codes([human(1), ai(2, authors=["A-9"])]), {"ai_with_authors": 1})
        mixed = ai(2, source_type="mixed", authors=[])
        self.assertEqual(self.codes([human(1), mixed]), {"missing_authors": 1})
        self.assertEqual(self.codes([human(1, source_type="unknown", authors=[])]), {})

    def test_derived_from_is_null_for_archive_documents(self):
        self.assertEqual(self.codes([human(1), human(2, derived_from="H-1")]), {"invalid_derived_from": 1})

    def test_derived_drafts_need_an_archive_parent_on_the_same_split(self):
        self.assertEqual(self.codes([ai(2, parent=None)]), {"missing_parent": 1})
        self.assertEqual(self.codes([ai(2, parent="H-404")]), {"missing_parent": 1})
        self.assertEqual(self.codes([human(1), ai(2), ai(3, parent="AI-2")]), {"missing_parent": 1})
        self.assertEqual(
            self.codes([human(1), ai(2, split="test")]), {"derived_split_mismatch": 1}
        )
        parent = human(1, source_type="unknown", date=None)
        self.assertEqual(self.codes([parent, ai(2)]), {})

    def test_derived_drafts_inherit_the_parent_license_and_use(self):
        self.assertEqual(
            self.codes([human(1), ai(2, license="CC0-1.0")]), {"license_differs_from_parent": 1}
        )
        parent = human(1, license="CC-BY-NC-4.0", use="internal")
        self.assertEqual(self.codes([parent, ai(2, license="CC-BY-NC-4.0", use="internal")]), {})
        child = ai(2, license="CC-BY-NC-4.0", use="product")
        self.assertEqual(
            self.codes([parent, child]), {"wrong_use": 1, "license_differs_from_parent": 1}
        )
        mixed = ai(2, source_type="mixed", authors=["A-9"], license="CC0-1.0")
        self.assertEqual(self.codes([human(1), mixed]), {"license_differs_from_parent": 1})

    def test_rejects_duplicate_ids_once_per_extra_record(self):
        dup = human(2, id="H-1")
        self.assertEqual(self.codes([human(1), dup]), {"duplicate_id": 1})

    def test_rejects_unsafe_paths(self):
        for path in ("/abs/x.txt", "../x.txt", "a/../../x.txt", "a\\b.txt", "", "a//b.txt", "./x.txt"):
            with self.subTest(path=path):
                self.assertEqual(self.codes([human(1, path=path)]), {"invalid_path": 1})

    def test_rejects_duplicate_paths(self):
        self.assertEqual(
            self.codes([human(1), human(2, path="persuade/H-1.txt")]), {"duplicate_path": 1}
        )

    def test_author_on_both_sides_of_the_split_leaks_once(self):
        records = [
            human(1, authors=["A-X"]), human(2, authors=["A-X"]),
            human(3, authors=["A-X"], split="test"), human(4, authors=["A-X"], split="test"),
        ]
        self.assertEqual(self.codes(records), {"split_leak_author": 1})

    def test_prompt_on_both_sides_of_the_split_leaks_once(self):
        records = [human(1, prompt="P-S"), human(2, prompt="P-S", split="test"),
                   human(3, prompt="P-S", split="test")]
        self.assertEqual(self.codes(records), {"split_leak_prompt": 1})

    def test_split_meta_must_name_a_date_and_a_method(self):
        for meta in (
            None, [], {}, {"test_split_date": "2026-01-15"}, {"method": "m"},
            {"test_split_date": "15/01/2026", "method": "m"},
            {"test_split_date": "2026-01-15", "method": ""},
            {**pinned([]), "extra": 1},
            {**pinned([]), "test_split_date": "9999-01-01"},
            {**pinned([]), "test_ids_sha256": "xyz"},
        ):
            with self.subTest(meta=meta):
                self.assertEqual(self.codes([], meta), {"invalid_split_meta": 1})

    def test_split_meta_without_the_test_hash_is_invalid(self):
        self.assertEqual(self.codes([human(1)], SPLIT), {"invalid_split_meta": 1})

    def test_test_split_date_may_be_today(self):
        today = datetime.date.today().isoformat()
        self.assertEqual(self.codes([], pinned([], test_split_date=today)), {})

    def test_test_split_is_pinned_to_its_ids(self):
        records = [human(1), human(2, split="test")]
        meta = pinned(records)
        self.assertEqual(self.codes(records, meta), {})
        moved = [human(1, split="test"), human(2, split="test")]
        self.assertEqual(self.codes(moved, meta), {"test_split_changed": 1})
        self.assertEqual(self.codes([human(1)], meta), {"test_split_changed": 1})


class DataDirTests(unittest.TestCase):
    def test_verifies_text_files_when_a_data_dir_is_given(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "persuade").mkdir()
            text = b"an essay"
            (root / "persuade" / "H-1.txt").write_bytes(text)
            good = human(1, sha256=hashlib.sha256(text).hexdigest())
            _, errors = check([good], pinned([good]), root)
            self.assertEqual(dict(errors), {})
            _, errors = check([human(1)], pinned([]), root)
            self.assertEqual(dict(errors), {"sha256_mismatch": 1})
            _, errors = check([human(2)], pinned([]), root)
            self.assertEqual(dict(errors), {"missing_file": 1})


class CliTests(unittest.TestCase):
    def run_checker(self, manifest_text, split="pinned", extra_args=()):
        if split == "pinned":
            try:
                split = pinned([json.loads(l) for l in manifest_text.splitlines() if l.strip()])
            except ValueError:
                split = SPLIT
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manifest.jsonl").write_text(manifest_text, encoding="utf-8")
            if split is not None:
                (root / "split.json").write_text(json.dumps(split), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER), str(root / "manifest.jsonl"), *extra_args],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.stderr, "")
        return result.returncode, json.loads(result.stdout)

    def test_passing_manifest_uses_the_split_file_next_to_it(self):
        lines = "\n".join(json.dumps(r) for r in [human(1), ai(2)]) + "\n"
        exit_code, report = self.run_checker(lines)
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            report,
            {"result": "passed", "counts": {"dev": {"human": 1, "ai": 1}, "test": {}}, "errors": {}},
        )

    def test_empty_manifest_passes(self):
        exit_code, report = self.run_checker("")
        self.assertEqual((exit_code, report["result"]), (0, "passed"))

    def test_report_never_contains_record_contents(self):
        secret = human(1, source_ref="SECRET-REF", license="MIT")
        exit_code, report = self.run_checker(json.dumps(secret))
        self.assertEqual((exit_code, report["errors"]), (1, {"unknown_license": 1}))
        self.assertNotIn("SECRET-REF", json.dumps(report))

    def test_missing_split_file_fails(self):
        exit_code, report = self.run_checker(json.dumps(human(1)), split=None)
        self.assertEqual(exit_code, 1)
        self.assertEqual(report["errors"], {"invalid_split_meta": 1})

    def test_unreadable_manifest_fails(self):
        for text in ("{not json}\n", '{"id": "H-1", "id": "H-2"}\n'):
            with self.subTest(text=text):
                exit_code, report = self.run_checker(text)
                self.assertEqual(exit_code, 1)
                self.assertEqual(report, {"result": "failed", "errors": {"unreadable_manifest": 1}})

    def test_data_dir_option_verifies_files(self):
        with tempfile.TemporaryDirectory() as data:
            exit_code, report = self.run_checker(
                json.dumps(human(1)), extra_args=("--data-dir", data)
            )
        self.assertEqual((exit_code, report["errors"]), (1, {"missing_file": 1}))


if __name__ == "__main__":
    unittest.main()
