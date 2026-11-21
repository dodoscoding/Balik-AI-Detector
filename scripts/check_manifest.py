"""Check the corpus manifest without printing any record's contents."""

import argparse
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus_rules import (  # noqa: E402
    ARCHIVE_TYPES, HUMAN, HUMAN_CUTOFF, AI, MIXED, INTERNAL_LICENSES, LANGUAGES, PRODUCT_LICENSES,
    REGISTERS, SOURCE_TYPES, SOURCES, SPLITS, TEST, USE_INTERNAL, USE_PRODUCT, USES, WRITING_CONTEXTS,
    is_code,
)


FIELDS = {
    "id", "source", "source_ref", "license", "use", "date", "source_type", "register",
    "population", "language", "writing_context", "authors", "prompt", "split", "path",
    "sha256", "derived_from",
}
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
SHA256 = re.compile(r"[0-9a-f]{64}")


def is_text(value):
    return isinstance(value, str) and value.strip() != ""


def is_date(value):
    if not isinstance(value, str) or DATE.fullmatch(value) is None:
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def has_valid_shape(record):
    """Return True when every field has an acceptable type and format."""
    if not isinstance(record, dict) or set(record) != FIELDS:
        return False
    date = record["date"]
    authors = record["authors"]
    return (
        is_code(record["id"])
        and is_text(record["source_ref"])
        and record["use"] in USES
        and (is_date(date) or (date is None and record["source_type"] in ARCHIVE_TYPES))
        and record["source_type"] in SOURCE_TYPES
        and record["register"] in REGISTERS
        and is_text(record["population"])
        and record["language"] in LANGUAGES
        and record["writing_context"] in WRITING_CONTEXTS
        and isinstance(authors, list)
        and all(is_code(author) for author in authors)
        and is_code(record["prompt"])
        and record["split"] in SPLITS
        and isinstance(record["path"], str)
        and isinstance(record["sha256"], str)
        and SHA256.fullmatch(record["sha256"]) is not None
        and (record["derived_from"] is None or isinstance(record["derived_from"], str))
    )


def check_record(record, errors):
    if record["source"] not in SOURCES:
        errors["unknown_source"] += 1
    if record["license"] in PRODUCT_LICENSES:
        expected_use = USE_PRODUCT
    elif record["license"] in INTERNAL_LICENSES:
        expected_use = USE_INTERNAL
    else:
        errors["unknown_license"] += 1
        expected_use = None
    if expected_use and record["use"] != expected_use:
        errors["wrong_use"] += 1


def is_safe_path(path):
    return "\\" not in path and all(part not in ("", ".", "..") for part in path.split("/"))


def test_ids_digest(records):
    """SHA-256 of the sorted test-split ids joined by newlines."""
    ids = sorted(record["id"] for record in records if record["split"] == TEST)
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()


def check_split_meta(split_meta, valid, errors):
    if not (
        isinstance(split_meta, dict)
        and set(split_meta) == {"test_split_date", "method", "test_ids_sha256"}
        and is_date(split_meta["test_split_date"])
        and split_meta["test_split_date"] <= datetime.date.today().isoformat()
        and is_text(split_meta["method"])
        and isinstance(split_meta["test_ids_sha256"], str)
        and SHA256.fullmatch(split_meta["test_ids_sha256"]) is not None
    ):
        errors["invalid_split_meta"] += 1
    elif split_meta["test_ids_sha256"] != test_ids_digest(valid):
        errors["test_split_changed"] += 1


def check_files(valid, data_dir, errors):
    seen = set()
    for record in valid:
        path = record["path"]
        if not is_safe_path(path):
            errors["invalid_path"] += 1
        elif path in seen:
            errors["duplicate_path"] += 1
        else:
            seen.add(path)
            if data_dir is not None:
                check_file(record, Path(data_dir) / path, errors)


def check_file(record, file_path, errors):
    try:
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    except OSError:
        errors["missing_file"] += 1
        return
    if digest != record["sha256"]:
        errors["sha256_mismatch"] += 1


def check_split_leaks(valid, errors):
    for field, code in (("authors", "split_leak_author"), ("prompt", "split_leak_prompt")):
        sides = {split: set() for split in SPLITS}
        for record in valid:
            values = record[field] if field == "authors" else [record[field]]
            sides[record["split"]].update(values)
        errors[code] += len(sides["dev"] & sides["test"])


def check_provenance(record, by_id, errors):
    source_type = record["source_type"]
    date = record["date"]
    if source_type == HUMAN:
        if date is None:
            errors["human_without_date"] += 1
        elif date >= HUMAN_CUTOFF:
            errors["human_after_cutoff"] += 1
    if source_type == AI and record["authors"]:
        errors["ai_with_authors"] += 1
    if source_type in (HUMAN, MIXED) and not record["authors"]:
        errors["missing_authors"] += 1

    parent_id = record["derived_from"]
    if source_type in ARCHIVE_TYPES:
        if parent_id is not None:
            errors["invalid_derived_from"] += 1
        return
    parent = by_id.get(parent_id)
    if parent is None or parent["source_type"] not in ARCHIVE_TYPES:
        errors["missing_parent"] += 1
        return
    if parent["split"] != record["split"]:
        errors["derived_split_mismatch"] += 1
    if parent["license"] != record["license"] or parent["use"] != record["use"]:
        errors["license_differs_from_parent"] += 1


def check(records, split_meta, data_dir=None):
    counts = {split: Counter() for split in SPLITS}
    errors = Counter()
    valid = []
    for record in records:
        if has_valid_shape(record):
            valid.append(record)
        else:
            errors["invalid_record"] += 1

    by_id = {}
    for record in valid:
        if record["id"] in by_id:
            errors["duplicate_id"] += 1
        else:
            by_id[record["id"]] = record
    for record in valid:
        counts[record["split"]][record["source_type"]] += 1
        check_record(record, errors)
        check_provenance(record, by_id, errors)
    check_files(valid, data_dir, errors)
    check_split_leaks(valid, errors)
    check_split_meta(split_meta, valid, errors)
    errors += Counter()  # drop zero entries
    return {split: dict(c) for split, c in counts.items()}, errors


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def load_json(text):
    return json.loads(text, object_pairs_hook=_unique_object)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--split", type=Path, help="default: split.json next to the manifest")
    parser.add_argument("--data-dir", type=Path, help="also verify each text file and its hash")
    args = parser.parse_args()
    try:
        lines = args.manifest.read_text(encoding="utf-8").splitlines()
        records = [load_json(line) for line in lines if line.strip()]
    except (OSError, ValueError):
        print(json.dumps({"result": "failed", "errors": {"unreadable_manifest": 1}}))
        return 1
    try:
        split_path = args.split or args.manifest.with_name("split.json")
        split_meta = load_json(split_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        split_meta = None

    counts, errors = check(records, split_meta, args.data_dir)
    print(json.dumps({
        "result": "failed" if errors else "passed",
        "counts": counts,
        "errors": errors,
    }, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
