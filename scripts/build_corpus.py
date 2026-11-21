"""Build the development corpus: texts under data/, manifest and split record under corpus/.

Raw downloads are untrusted data. They are parsed here, never executed.
"""

import argparse
import collections
import csv
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import corpus_sources
from corpus_rules import HUMAN_CUTOFF, TEST
from corpus_split import assign_split

ROOT = Path(__file__).resolve().parents[1]
PERSUADE_PUBLISHED_BY = "2022-03-25"
OAI_URL = (
    "https://oaipmh.arxiv.org/oai?verb=GetRecord&identifier=oai:arXiv.org:{id}&metadataPrefix=arXiv"
)
OAI_DELAY_SECONDS = 3.0
USER_AGENT = "corpus-builder (research; cached, 1 request per 3 s)"


class SplitChangedError(Exception):
    """The test ids differ from the ones pinned in an existing split.json."""


def test_ids_digest(ids):
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def read_persuade(csv_path):
    """Yield one row per essay from the long-format PERSUADE CSV."""
    csv.field_size_limit(sys.maxsize)
    seen = set()
    with open(csv_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            essay = row.get("essay_id_comp")
            if essay and essay not in seen:
                seen.add(essay)
                yield row


def sample_persuade(rows, per_prompt, seed):
    """Take up to per_prompt essays from every prompt, chosen by the seed."""
    by_prompt = collections.defaultdict(list)
    for row in rows:
        by_prompt[row["prompt_name"]].append(row)
    chosen = []
    for prompt in sorted(by_prompt):
        pool = sorted(by_prompt[prompt], key=lambda row: row["essay_id_comp"])
        random.Random(f"{seed}:{prompt}").shuffle(pool)
        chosen.extend(pool[:per_prompt])
    return chosen


def read_shard_candidates(shard_path):
    """Yield unverified arXiv candidates from a Common Pile shard."""
    with gzip.open(shard_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            created = str(record.get("created") or "")[:10]
            if not created or created >= HUMAN_CUTOFF:
                continue
            candidate = corpus_sources.common_pile_candidate(record)
            if candidate:
                yield candidate


def cached_oai_fetcher(cache_dir, delay=OAI_DELAY_SECONDS):
    """Return fetch(arxiv_id) -> XML text or None, one request per `delay` s, cached on disk."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    last_request = [0.0]

    def fetch(arxiv_id):
        cache_file = cache_dir / (arxiv_id.replace("/", "_") + ".xml")
        if cache_file.exists():
            return cache_file.read_text(encoding="utf-8")
        url = OAI_URL.format(id=urllib.parse.quote(arxiv_id, safe="/"))
        for attempt in range(5):
            wait = delay - (time.monotonic() - last_request[0])
            if wait > 0:
                time.sleep(wait)
            last_request[0] = time.monotonic()
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=60) as response:
                    body = response.read().decode("utf-8")
                cache_file.write_text(body, encoding="utf-8")
                return body
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    return None
                retry = error.headers.get("Retry-After")
                time.sleep(float(retry) if retry and retry.isdigit() else delay * (attempt + 2))
            except (urllib.error.URLError, TimeoutError):
                time.sleep(delay * (attempt + 2))
        return None

    return fetch


def select_arxiv(shards, count, seed, fetch_oai):
    """Verify candidates against arXiv, in seed order, until `count` pass."""
    candidates = {}
    for shard in shards:
        for candidate in read_shard_candidates(shard):
            candidates.setdefault(candidate["arxiv_id"], candidate)
    ordered = [candidates[key] for key in sorted(candidates)]
    random.Random(seed).shuffle(ordered)
    documents, rejected = [], collections.Counter()
    candidates_found = len(candidates)
    for candidate in ordered:
        if len(documents) >= count:
            break
        xml_text = fetch_oai(candidate["arxiv_id"])
        if xml_text is None:
            rejected["oai_unavailable"] += 1
            continue
        verified = corpus_sources.verify_oai(corpus_sources.parse_oai(xml_text))
        if verified is None:
            rejected["oai_rejected"] += 1
            continue
        documents.append(corpus_sources.arxiv_document(candidate, *verified))
    return documents, rejected, candidates_found


def build(
    persuade_csv, arxiv_shards, data_dir, manifest_path, split_path, per_prompt, arxiv_count,
    test_fraction, seed, today, fetch_oai,
):
    data_dir = Path(data_dir)
    documents = []
    if persuade_csv:
        rows = sample_persuade(read_persuade(persuade_csv), per_prompt, seed)
        for row in rows:
            document = corpus_sources.persuade_document(row, PERSUADE_PUBLISHED_BY)
            if document:
                documents.append(document)
    persuade_count = len(documents)
    if arxiv_shards:
        arxiv_documents, rejected, candidates_found = select_arxiv(
            arxiv_shards, arxiv_count, seed, fetch_oai
        )
    else:
        arxiv_documents, rejected, candidates_found = [], collections.Counter(), 0
    documents.extend(arxiv_documents)

    split = {}
    for source in sorted({fields["source"] for fields, _ in documents}):
        group = [fields for fields, _ in documents if fields["source"] == source]
        split.update(assign_split(group, test_fraction, seed))

    test_digest = test_ids_digest(ident for ident, side in split.items() if side == TEST)
    split_path = Path(split_path)
    if split_path.exists():  # the test set is reserved once; keep its date and refuse to change it
        pinned = json.loads(split_path.read_text(encoding="utf-8"))
        if pinned.get("test_ids_sha256", test_digest) != test_digest:
            raise SplitChangedError(
                f"the test set would change, but {split_path} already reserves it; "
                "delete the split file only to start a new corpus"
            )
        today = pinned["test_split_date"]

    rows = []
    for fields, text in documents:
        path = f"{fields['source']}/{fields['id']}.txt"
        target = data_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="")
        rows.append({**fields, "split": split[fields["id"]], "path": path, "sha256": corpus_sources.sha256_text(text)})
    rows.sort(key=lambda row: row["id"])

    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    method = (
        "Documents sharing an author code or a prompt code, directly or through a chain, form one group "
        "(union-find). Each source is split separately: whole groups, in seeded random order, go to test "
        f"until test holds {test_fraction:.0%} of that source's documents. seed={seed}."
    )
    split_path.write_text(
        json.dumps(
            {"test_split_date": today, "method": method, "test_ids_sha256": test_digest}, indent=2
        ) + "\n", encoding="utf-8"
    )
    counts = collections.Counter((row["source"], row["source_type"], row["split"]) for row in rows)
    return {
        "persuade": persuade_count,
        "arxiv": len(arxiv_documents),
        "arxiv_candidates": candidates_found,
        "arxiv_rejected": dict(rejected),
        "by_source_type_split": {"/".join(key): n for key, n in sorted(counts.items())},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--persuade-csv", type=Path)
    parser.add_argument("--arxiv-shard", type=Path, action="append", default=[])
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--corpus-dir", type=Path, default=ROOT / "corpus")
    parser.add_argument("--per-prompt", type=int, default=50)
    parser.add_argument("--arxiv-count", type=int, default=300)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=20221130)
    args = parser.parse_args()
    try:
        report = build_from_args(args)
    except SplitChangedError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


def build_from_args(args):
    return build(
        persuade_csv=args.persuade_csv,
        arxiv_shards=args.arxiv_shard,
        data_dir=args.data_dir,
        manifest_path=args.corpus_dir / "manifest.jsonl",
        split_path=args.corpus_dir / "split.json",
        per_prompt=args.per_prompt,
        arxiv_count=args.arxiv_count,
        test_fraction=args.test_fraction,
        seed=args.seed,
        today=datetime.date.today().isoformat(),
        fetch_oai=cached_oai_fetcher(args.data_dir / "raw" / "arxiv" / "oai"),
    )


if __name__ == "__main__":
    raise SystemExit(main())
