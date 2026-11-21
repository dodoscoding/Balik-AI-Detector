# Balik AI Detector — Product Roadmap

Balik revises a draft so it reads as natural human writing. It covers human, AI-generated, and mixed drafts, and the writer can compare the result with the original. Balik starts as a free tool for friends. It may be sold later if it succeeds, so data and licensing follow product rules from the start. See [ADR 0003](docs/adr/0003-balik-revises-any-draft.md).

English academic writing comes first. Turkish and general writing wait until English academic passes the [friends gate](#delivery-milestones). Terms in this roadmap follow the [glossary](GLOSSARY.md).

## The first user journey

1. **Analyze a draft.** Paste text, confirm the language, and run detection. Show the assessment, its uncertainty, and sentence highlights when supported. Until provider access is funded, the assessment comes from the local detector set and is labeled that way. Explain when a sample is too short to assess.
2. **Revise the writing.** Choose an academic, conversational, or plain-language tone. Address repetition, unclear references, and awkward phrasing while preserving the draft's claims, quotations, citations, and numbers. When the draft has a writer, keep their distinctive wording, first-person choices, and discipline-specific terms where they fit the requested tone. Preserve deliberate uncertainty. Turning “may reduce risk” into “reduces risk” changes the claim. Leave passages that already meet the brief alone.
3. **Review the changes.** Show the original and revised passages side by side. Let the writer accept or reject edits before running detection again.
4. **Compare and export.** Run the same detector on the accepted version, show both assessments with their labels, and let the writer copy or download the final text.

## How we will evaluate the 3% target

The requested target is a post-edit result of **3% or less on both Turnitin and GPTZero**.

**Status: not measured.** Measuring requires paid access and each provider's written permission for this use. Both are deferred to [milestone 5](#delivery-milestones). Development uses the local detector set instead. Its scores are not Turnitin or GPTZero results and must never be reported as such. See [ADR 0002](docs/adr/0002-local-detectors-until-funded.md).

When milestone 5 runs, evaluate on held-out drafts with authorized access to each service. Record each provider's actual output, the date, and the model version when available.

| Provider | What to record | How to evaluate the target |
| --- | --- | --- |
| Turnitin | The AI Writing Report's percentage of qualifying prose flagged as likely AI-generated. The report displays `*%` for results from 1% through 19%. | A displayed 0% meets the target. A displayed 20% or higher exceeds it. An asterisk leaves the 3% threshold unresolved. [Turnitin reporting guide](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report) |
| GPTZero | The predicted document class and all three class probabilities (AI-only, mixed, and human-only). | The numeric check passes when the AI-only probability is ≤ 0.03. A result of 2% AI-only, 97% mixed, and 1% human-only passes that check and must be reported with the verdict “mixed.” [GPTZero score interpretation](https://support.gptzero.me/articles/4083713560-how-do-i-turn-the-probabilities-from-your-api-into-outcomes) |

For each language, publish counts of drafts that passed both checks, exceeded either threshold, or had an unresolved result. Count missing or unsupported scans explicitly and break out GPTZero verdicts among numeric passes. Turnitin's AI writing detection may not support Turkish. Confirm its language scope before planning a Turkish measurement, and record Turkish Turnitin results as unsupported if it does not. Limit detector claims to the tested sample. Base writing-quality claims and beta admission on the editorial evaluation below.

## Development data

Develop Balik on public archive text, not on drafts collected from friends. Friends take part only at the gate. See [ADR 0001](docs/adr/0001-public-archive-corpus.md).

- **Human-written text** is a document published or submitted before 30 November 2022. Treat anything later as unknown-origin text, never as human-written.
- **Licenses.** Text that reaches the product, such as few-shot examples, retrieval exemplars, or fine-tuning data, must allow commercial use: CC BY, CC0, or public domain. Research-only or non-commercial corpora may be used for internal measurement only, and only when their license explicitly allows it. Record the license of every document.
- **First English sources.**
  - PERSUADE 2.0 (CC BY 4.0) for student writing. Its writers are US students in grades 6–12, not university students; label it that way in every report.
  - arXiv papers whose metadata shows CC BY or CC0, or peS2o documents with a verified license, for published academic writing.
  - University-level student corpora such as BAWE or MICUSP only under a license that permits our use.
- **AI drafts and mixed drafts** are generated from the same prompt or source as each human document, so a comparison never differs by topic. Record the generating model, version, prompt, settings, machine, and runtime.
- **Excluded.** The Kaggle `AI Generated Essays Dataset.csv` is excluded. Its AI essays cover different topics from its human essays.
- **Storage.** Corpus text lives in the git-ignored `data/` folder or outside the repository. A committed manifest lists each document's source, license, date, register, source type, and split.

## Delivery milestones

| Milestone | Work | Completion check |
| --- | --- | --- |
| 1. Build the development corpus and detector baseline | Assemble the English corpus described above. Generate matching AI and mixed drafts. Split development and test sets by prompt and author, keeping every derived draft on its source's side. Reserve the test set before any comparison. Set up the local detector set: at least two zero-shot detectors, such as Binoculars and Fast-DetectGPT, and one classifier trained on permissively licensed human-vs-AI data, such as RAID (MIT) or MAGE (Apache-2.0). | A baseline report for each register gives each detector's false positives on human-written text, missed AI drafts, and results on mixed drafts, with denominators. The manifest covers every document. |
| 2. Develop the humanizer | Iterate on the revision approach with a pinned local 7–14B model. Compare every candidate with two baselines on the same model and settings: the basic copyedit and the naive humanizer. Free cloud tiers may be used on public-archive data only, with the provider recorded for each run. Fix the restraint and fidelity thresholds before the first run. | Keep a change only if, on held-out development drafts, it (1) lowers local detector scores on AI and mixed drafts on at least two detectors, (2) passes the automated fidelity check, and (3) leaves human-written documents within the restraint threshold. The milestone ends when a frozen Balik version beats both baselines on (1) while passing (2) and (3). Keep every failure as a regression case. |
| 3. Pass the friends gate | Run the blind comparison below with friends, using the existing [blind editing](docs/m1-blind-edits.md) and [draft split](docs/m1-draft-split.md) procedures. Include friends' own drafts and AI and mixed drafts from their assignment prompts. Keep local detector scores hidden until all votes are recorded. | Balik meets the preference, meaning, and restraint criteria, plus the voice criterion on drafts that have a writer. The 50-draft and 20-writer minimums do not apply. Report the counts as a friends rehearsal, not as beta evidence. If Balik misses a criterion, return to milestone 2. |
| 4. Build the editor | Implement paste → detect → revise → review → reanalyze → export. Keep the original draft available throughout the session. | A tester can complete the journey, reject an edit, and export the accepted text. A failed scan can be retried without losing edits. |
| 5. Measure with provider detectors and qualify for beta | Only after milestone 3 succeeds and funding is approved. Get each provider's terms for this use in writing. Freeze the revision approach and baselines. Run the 3% evaluation and the full blind comparison on the untouched test set. Add Turkish or general writing only after building their own corpus as in milestone 1. | Admit only language and writing context combinations that meet every beta criterion below. Record the counts, errors, and decision for each combination. If a provider refuses or access is not funded, record that provider as not measured and make no claims about it. |
| 6. Run a limited beta | Add usage limits, clear retention settings, and deletion controls for stored drafts. Measure completed editing sessions, failed scans, latency, and cost. | Verify deletion and recovery from provider failures. Use measured cost per completed session and beta feedback to decide pricing and whether to launch publicly. |

**Reference machine.** Every reported comparison runs on the reference Mac with its pinned runtime. The Windows PC may generate corpus drafts in bulk. Record its runtime in the manifest.

## Blind comparison and beta criteria

Use the same draft and tone request for every editor. For the basic copyedit, use a fixed prompt asking the same base model to correct grammar and improve clarity while preserving meaning and voice. For the naive humanizer, use a fixed prompt asking the same model to rewrite the draft so it sounds human-written. Save each prompt, the model version, and the settings so the comparison can be repeated. Keep each author and all versions of a draft on one side of the development/test split.

Give two reviewers fluent in the draft's language the original as a reference and both candidate edits in random order. Hide editor identities and detector scores. Have reviewers independently judge clarity, naturalness, and fit to the brief, then select the better edit or “equally good.” Ask a third blind reviewer to resolve disagreements. Record one outcome per draft, including ties. Include passages marked before editing as already meeting the brief, where leaving the original intact is the desired outcome.

Milestone 3 applies these criteria without the sample-size minimums. Milestone 5 applies them independently to each proposed language and writing context on at least 50 held-out drafts per combination.

| Criterion | Required result |
| --- | --- |
| Editorial preference | Reviewers prefer Balik over the basic copyedit on at least 65% of all drafts in the combination. Ties stay in the denominator. Report wins, ties, and losses. |
| Writer's voice | Applies only to drafts with an identifiable writer. AI drafts have none. Ask participating writers, with editor identities hidden, “Would you publish this version without editing it to sound like you again?” Collect paired answers for both versions of each writer's own draft from at least 20 distinct writers per combination, one draft per writer. At least 80% must answer yes for Balik. Report both rates. |
| Meaning and restraint | Review every Balik output against its source. Any changed factual claim, attribution, quantity, quotation, citation, or degree of certainty blocks that combination. Include at least 10 passages per combination marked as already meeting the brief. Balik must leave at least 9 of those 10 unchanged (90% if more are included). |

At the minimum beta sample size, an English academic pilot needs at least 33 wins across 50 drafts, 16 yes responses from 20 writers, zero meaning-changing errors, and 9 of 10 already-polished passages left unchanged. A result of 32 wins and 18 ties misses the preference threshold even if every other criterion passes. Record the decision for English academic writing separately from the other pilot audiences.

If a combination misses a criterion or lacks enough observations, keep it out of beta. Use discovered failures as regression cases. After changing the revision approach, run the full comparison for the affected combination on fresh held-out drafts before reconsidering it.
