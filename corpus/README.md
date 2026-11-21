# Development corpus

The English development corpus of [ADR 0001](../docs/adr/0001-public-archive-corpus.md): PERSUADE 2.0 student essays and the introductions of arXiv papers. Only `manifest.jsonl` and `split.json` are committed; the texts live in the git-ignored `data/` folder.

PERSUADE writers are US students in grades 6-12, not university students. Say so in every report.

Rebuild (needs Python 3 and curl; the arXiv check takes about 15 minutes because arXiv allows one request per 3 seconds):

    scripts/fetch_corpus.sh
    python3 scripts/build_corpus.py --persuade-csv data/raw/persuade-2.0/train.csv --arxiv-shard data/raw/arxiv/00000_arxiv-papers.jsonl.gz
    python3 scripts/check_manifest.py corpus/manifest.jsonl --data-dir data

- **Date.** Human-written means dated before 30 November 2022. PERSUADE essays carry the date 2022-03-25. This is a corpus-level "published by" date, not a per-essay date: it is the first commit of the PERSUADE 1.0 repository, and every essay in the train CSV is Kaggle Feedback Prize 2021 data. arXiv papers carry the date of their latest version in arXiv's own metadata.
- **License.** Only CC BY, CC0 and public domain enter, so every document has `use: product`. PERSUADE 2.0 is CC BY 4.0 according to the README of github.com/scrosseye/persuade_corpus_2.0. Each arXiv paper's license is checked against arXiv's OAI-PMH record, not just the Common Pile metadata.
- **Split.** Documents sharing an author or prompt code stay on one side; `split.json` records the date the test set was reserved and how.
- **Rules.** The allowed values, the date cutoff and the license lists live in `scripts/corpus_rules.py`; the builder and `check_manifest.py` both import them. `split.json` also pins the test ids with a SHA-256, so the checker reports `test_split_changed` if the test set moves, and the builder refuses to rewrite it.

## Known limits

- PERSUADE 2.0 has no student id column, so each essay gets its own author code and the split separates PERSUADE by prompt only.
- arXiv author codes hash normalized name strings, so variant spellings of one person ("J. Smith" and "John Smith") are not linked.
