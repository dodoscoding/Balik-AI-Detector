# M1 blind editing runbook

This runbook is for the operator, who does not take part in the vote. The rehearsal coordinator receives the same ballot as the other reviewers. Keep the A/B key sealed until all peer and writer responses and any deciding votes have been recorded. See [issue #12](https://github.com/dodoscoding/Balik-AI-Detector/issues/12) and [the comparison criteria](../ROADMAP.md#blind-comparison-and-beta-criteria).

## Run the synthetic example

Use a Mac with Apple silicon and `uv`. The pinned local model takes about 0.9 GB of disk space. The example brief contains a fictional survey, citation, and quotation. [Model card](https://huggingface.co/mlx-community/Qwen2.5-1.5B-Instruct-4bit) · [MLX LM](https://github.com/ml-explore/mlx-lm)

Run these commands from the repository root. The model download is a one-time setup step.

```sh
HF_HUB_DISABLE_TELEMETRY=1 uvx --python 3.12 --from huggingface-hub hf download \
  mlx-community/Qwen2.5-1.5B-Instruct-4bit \
  --revision 8b403126fc14f14cfc99bb4cfa72ecbc129ea677
mkdir -p -m 700 "$HOME/.local/share/balik-evaluation"
uv run --script scripts/blind_edits.py examples/academic-brief.json \
  "$HOME/.local/share/balik-evaluation/example-01"
```

Before sharing any `ballot.txt`, read both anonymous versions. Each must contain only draft text, with no editor labels, model identity, run details, or detector scores. Withhold the ballot if any of those appear. The ballot contains the assignment, writing goal, tone, original, both anonymous edits, and a question for the reviewer.

Share only `ballot.txt` once it passes that check. The run directory and `private.json` stay with the operator. The private record contains both full instructions, their shared input, the pinned model revision, runtime versions, settings, A/B key, run date, per-edit and total elapsed time, original word count, and service fee. Elapsed time includes model loading and generation. The service fee is USD 0 and excludes hardware, electricity, and setup time.

For a permissioned rehearsal draft, create the same four-field JSON brief outside the repository. Keep any passage marked by the writer in a separate record. Use a new directory named with the coded draft ID. A fresh run randomly assigns the labels again. Archive the exact ballot and private record from the same run together.

## Check the synthetic ballot before sharing it

Read the original and each version against these reference points. They are for the operator's fidelity check.

| Check | Original to compare |
| --- | --- |
| Claim and scope | The responses concern a potential benefit for the students sampled. One stop on one evening limits broader applicability. |
| Attribution and citation | `(Lee, 2024)` and `Lee (2024, p. 7)` |
| Quotation | `"a dry place to wait."` |
| Quantities | `18 students`, `the same two questions`, `one stop`, and `a single evening` |
| Degree of certainty | `may make the evening bus easier to use` |
| Voice and restraint | `I kept that boundary visible because the quietest answers mattered too.` |
