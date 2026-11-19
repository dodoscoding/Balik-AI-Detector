# Balik AI Detector — Product Roadmap

Balik will help writers inspect a draft for signs of AI-generated writing, revise it in their own voice, and compare the result with the original. The proposed pilot covers English and Turkish. It will include both academic and general writing so we can choose the first audience based on results.

## The first user journey

1. **Analyze a draft.** Paste text, confirm the language, and run detection. Show the detector's assessment, its uncertainty, and sentence highlights when supported. Explain when a sample is too short to assess.
2. **Revise the writing.** Choose an academic, conversational, or plain-language tone. The humanizer should address repetition, unclear references, and awkward phrasing while preserving the writer's claims, quotations, citations, and numbers.
3. **Review the changes.** Show the original and revised passages side by side. Let the writer accept or reject edits before running detection again.
4. **Compare and export.** Run the same detector on the accepted version, show both assessments with their labels, and let the writer copy or download the final text.

## How we will evaluate the 3% target

The requested target is a post-edit result of **3% or less on both Turnitin and GPTZero**. Evaluate it on held-out drafts with authorized access to each service. Record each provider's actual output, the date, and the model version when available.

| Provider | What to record | How to evaluate the target |
| --- | --- | --- |
| Turnitin | The AI Writing Report's percentage of qualifying prose flagged as likely AI-generated. The report displays `*%` for results from 1% through 19%. | A displayed 0% meets the target. A displayed 20% or higher exceeds it. An asterisk leaves the 3% threshold unresolved. [Turnitin reporting guide](https://guides.turnitin.com/hc/en-us/articles/28457596598925-How-to-access-the-AI-Writing-Report) |
| GPTZero | The probabilities assigned to the AI, mixed, and human classes for the document. | Use the AI-class probability ≤ 0.03 as the proposed threshold and retain the mixed-class probability alongside it so readers can interpret the result. [GPTZero score interpretation](https://support.gptzero.me/articles/4083713560-how-do-i-turn-the-probabilities-from-your-api-into-outcomes) |

For each language, publish counts of drafts that passed both checks, exceeded either threshold, or had an unresolved result. Count missing or unsupported scans explicitly. Report observations for the tested sample only. A lower score counts as a successful edit only if the revision also preserves meaning.

## Delivery milestones

| Milestone | Work | Completion check |
| --- | --- | --- |
| 1. Establish a baseline | Assemble permissioned human-written, AI-generated, and mixed drafts. Include both languages and both writing contexts. Set aside a test set before comparing detection and revision options. | Report false positives on human writing, missed AI drafts, mixed results, response time, and cost per 1,000 words by language. Choose the first audience and supported language coverage from the pilot. |
| 2. Build the editor | Implement paste → detect → revise → review → reanalyze → export. Keep the original draft available throughout the session. | A tester can complete the journey, reject an edit, and export the accepted text. A failed scan can be retried without losing edits. |
| 3. Validate the revisions | Have bilingual reviewers compare original and revised passages with detector scores hidden. Check factual claims, quotations, citations, quantities, and tone. Run the external benchmark on eligible held-out samples. | Report how often reviewers prefer the revision and list meaning-changing errors. Fix critical errors and repeat the affected checks before inviting beta users. |
| 4. Run a limited beta | Add usage limits, clear retention settings, and deletion controls for stored drafts. Measure completed editing sessions, failed scans, latency, and cost. | Verify deletion and recovery from provider failures. Use measured cost per completed session and beta feedback to decide pricing and whether to launch publicly. |

The first deliverable is the baseline report. It should identify which detector and revision approach to use, which writing audience benefits most, and where the available evidence supports a user-facing claim.
