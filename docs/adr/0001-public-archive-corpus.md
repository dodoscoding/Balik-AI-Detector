# Develop on public-archive text; writers only at the gate

The first milestone asked friends for permissioned drafts and used them to develop and judge Balik. That gave too little text to develop against, and it mixed private drafts into every experiment. We develop Balik on public-archive text instead, generate matching AI drafts and mixed drafts from the same prompts, and bring friends in only at the friends gate. That gate still needs living writers for the voice criterion.

Two rules make archive text usable.

- **Date.** Text counts as human-written only if it was published or submitted before 30 November 2022. Later public text is unknown-origin text.
- **License.** Anything that reaches the product, such as few-shot examples, retrieval exemplars, or fine-tuning data, must allow commercial use: CC BY, CC0, or public domain. Research-only and non-commercial corpora serve internal measurement only, and only when their license allows it. Balik is free for friends today but may be sold, and re-sourcing data later would be costly.

## Consequences

- Commercially licensed student writing is scarce. The first student corpus, PERSUADE 2.0, comes from US grades 6–12, so reports must not present it as university writing.
- University-level student text needs a license such as BAWE's, or friends' consent at the gate.
- Turkish has no student corpus and few clearly licensed academic sources. Turkish work waits until English academic writing passes the friends gate.
- Public text removes the privacy constraint on development data, so free cloud model tiers are allowed on it. Friends' drafts stay on local models.
- Topic-mismatched human-vs-AI sets, such as the Kaggle `AI Generated Essays Dataset.csv`, are excluded. A comparison on them would measure topic, not style.
