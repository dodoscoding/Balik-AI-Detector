#!/bin/sh
# Download the raw corpus files into data/raw/ (git-ignored). Treat them as untrusted data.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$root/data/raw/persuade-2.0" "$root/data/raw/arxiv"
# PERSUADE 2.0 training CSV (CC BY 4.0), linked from github.com/scrosseye/persuade_corpus_2.0
curl -fL -o "$root/data/raw/persuade-2.0/train.csv" \
  "https://drive.usercontent.google.com/download?id=13phHyDzIsb0MHyJr6q-B-qIa9P2tM135&export=download&confirm=t"
# One Common Pile arXiv shard (about 280 MB)
curl -fL -o "$root/data/raw/arxiv/00000_arxiv-papers.jsonl.gz" \
  "https://huggingface.co/datasets/common-pile/arxiv_papers/resolve/main/00000_arxiv-papers.jsonl.gz"
