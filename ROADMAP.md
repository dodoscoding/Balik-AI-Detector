# Balik AI Detector — Product Roadmap

Balik will help writers inspect a draft for signs of AI-generated writing, revise it in their own voice, and compare the result with the original. The proposed pilot covers English and Turkish. It will include both academic and general writing so we can choose the first audience based on results.

## The first user journey

1. **Analyze a draft.** Paste text, confirm the language, and run detection. Show the detector's assessment, its uncertainty, and sentence highlights when supported. Explain when a sample is too short to assess.
2. **Revise the writing.** Choose an academic, conversational, or plain-language tone. Address repetition, unclear references, and awkward phrasing while preserving the writer's claims, quotations, citations, and numbers. Keep distinctive wording, first-person choices, and discipline-specific terms where they fit the requested tone. Preserve deliberate uncertainty. Turning “may reduce risk” into “reduces risk” changes the claim. Leave passages that already meet the brief alone.
3. **Review the changes.** Show the original and revised passages side by side. Let the writer accept or reject edits before running detection again.
4. **Compare and export.** Run the same detector on the accepted version, show both assessments with their labels, and let the writer copy or download the final text.

## How we will evaluate the 3% target

The requested target is a post-edit result of **3% or less on both Turnitin and GPTZero**. Evaluate it on held-out drafts with authorized access to each service. Record each provider's actual output, the date, and the model version when available.

| Provider | What to record | How to evaluate the target |
| --- | --- | --- |
| Turnitin | The AI Writing Report's percentage of qualifying prose flagged as likely AI-generated. The report displays `*%` for results from 1% through 19%. | A displayed 0% meets the target. A displayed 20% or higher exceeds it. An asterisk leaves the 3% threshold unresolved. [Turnitin reporting guide](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report) |
| GPTZero | The predicted document class and all three class probabilities (AI-only, mixed, and human-only). | The numeric check passes when the AI-only probability is ≤ 0.03. A result of 2% AI-only, 97% mixed, and 1% human-only passes that check and must be reported with the verdict “mixed.” [GPTZero score interpretation](https://support.gptzero.me/articles/4083713560-how-do-i-turn-the-probabilities-from-your-api-into-outcomes) |

For each language, publish counts of drafts that passed both checks, exceeded either threshold, or had an unresolved result. Count missing or unsupported scans explicitly and break out GPTZero verdicts among numeric passes. Limit detector claims to the tested sample. Base writing-quality claims and beta admission on the editorial evaluation below.

## Delivery milestones

| Milestone | Work | Completion check |
| --- | --- | --- |
| 1. Test whether Balik beats a basic copyedit | Assemble permissioned human-written, AI-generated, and mixed drafts across English and Turkish, academic and general writing. Reserve the final test set before comparing approaches. Run the blind comparison below on development drafts before building the full editor. | The baseline report names each language and writing context where Balik meets the preference, voice, and fidelity targets on development drafts. Build for a qualifying audience. If none qualifies, revise the approach and repeat milestone 1. Also report detector false positives on human writing, missed AI drafts, mixed results, response time, and cost per 1,000 words by language. |
| 2. Build the editor | Implement paste → detect → revise → review → reanalyze → export. Keep the original draft available throughout the session. | A tester can complete the journey, reject an edit, and export the accepted text. A failed scan can be retried without losing edits. |
| 3. Qualify for beta | Freeze the chosen revision approach and basic copyedit. Repeat the same blind comparison on the untouched final test set. Run the external benchmark on eligible held-out drafts. | Admit only language and writing context combinations that meet every beta criterion below. Record the counts, errors, and decision for each combination. |
| 4. Run a limited beta | Add usage limits, clear retention settings, and deletion controls for stored drafts. Measure completed editing sessions, failed scans, latency, and cost. | Verify deletion and recovery from provider failures. Use measured cost per completed session and beta feedback to decide pricing and whether to launch publicly. |

## Blind comparison and beta criteria

Use the same draft and tone request for both editors. For the basic copyedit, use a fixed prompt asking the same base model to correct grammar and improve clarity while preserving meaning and voice. Save the prompt, model version, and settings so the comparison can be repeated. Keep each author and all versions of a draft on one side of the development/test split.

Give two reviewers fluent in the draft's language the original as a reference and both candidate edits in random order. Hide editor identities and detector scores. Have reviewers independently judge clarity, naturalness, and fit to the brief, then select the better edit or “equally good.” Ask a third blind reviewer to resolve disagreements. Record one outcome per draft, including ties. Include passages marked before editing as already meeting the brief, where leaving the original intact is the desired outcome.

Use these proposed pilot thresholds in milestone 1 and fix them before scoring. For beta, apply them independently to each proposed language and writing context on at least 50 held-out drafts per combination.

| Criterion | Required result |
| --- | --- |
| Editorial preference | Reviewers prefer Balik over the basic copyedit on at least 65% of all drafts in the combination. Ties stay in the denominator. Report wins, ties, and losses. |
| Writer's voice | Ask participating writers, with editor identities hidden, “Would you publish this version without editing it to sound like you again?” Collect paired answers for both versions of each writer's own draft from at least 20 distinct writers per combination, one draft per writer. At least 80% must answer yes for Balik. Report both rates. |
| Meaning and restraint | Review every Balik output against its source. Any changed factual claim, attribution, quantity, quotation, citation, or degree of certainty blocks that combination. Include at least 10 passages per combination marked as already meeting the brief. Balik must leave at least 9 of those 10 unchanged (90% if more are included). |

If a combination misses a criterion or lacks enough observations, keep it out of beta. Use discovered failures as regression cases. After changing the revision approach, run the full comparison for the affected combination on fresh held-out drafts before reconsidering it.
