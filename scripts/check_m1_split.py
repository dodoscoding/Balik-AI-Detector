"""Check a private, coded assignment register without printing its records."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re


GROUPS = ("rehearsal", "final")
CODE = re.compile(r"[A-Z][A-Z0-9_-]{2,63}")


def is_code(value):
    return isinstance(value, str) and CODE.fullmatch(value) is not None


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def check(register):
    counts = {group: Counter(authors=0, drafts=0) for group in GROUPS}
    errors = Counter()
    authors = set()
    records = set()
    if not isinstance(register, dict) or set(register) != set(GROUPS):
        errors["invalid_register"] += 1
        return counts, errors

    for group in GROUPS:
        rows = register[group]
        if not isinstance(rows, list):
            errors["invalid_group"] += 1
            continue

        group_authors = set()
        group_drafts = set()
        for row in rows:
            fields = {"author", "draft", "related", "peer_permission", "cloud_permission"}
            if not isinstance(row, dict) or set(row) != fields:
                errors["invalid_record"] += 1
                continue

            author = row["author"]
            if not is_code(author):
                errors["invalid_author_code"] += 1
            elif author in authors:
                errors["reused_author_code"] += 1
                group_authors.add(author)
            else:
                authors.add(author)
                group_authors.add(author)

            if is_code(row["draft"]):
                group_drafts.add(row["draft"])

            related = row["related"]
            if not isinstance(related, list):
                errors["invalid_related_records"] += 1
                related = []
            for code in [row["draft"], *related]:
                if not is_code(code):
                    errors["invalid_artifact_code"] += 1
                elif code in records:
                    errors["reused_artifact_code"] += 1
                else:
                    records.add(code)

            if row["peer_permission"] is not True:
                errors["missing_peer_permission"] += 1
            if row["cloud_permission"] not in ("not_requested", "declined", "granted"):
                errors["invalid_cloud_permission"] += 1

        counts[group]["authors"] = len(group_authors)
        counts[group]["drafts"] = len(group_drafts)
        expected = (4,) if group == "rehearsal" else (3, 4)
        if len(rows) not in expected:
            errors["unexpected_group_size"] += 1

    return counts, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("register", type=Path)
    args = parser.parse_args()
    try:
        register = json.loads(
            args.register.read_text(encoding="utf-8"), object_pairs_hook=_unique_object
        )
    except (OSError, ValueError):
        print(json.dumps({"result": "failed", "errors": {"unreadable_register": 1}}))
        return 1

    counts, errors = check(register)
    print(json.dumps({
        "result": "failed" if errors else "passed",
        "counts": counts,
        "errors": errors,
    }, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
