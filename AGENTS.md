## Agent skills

### Humanizer evaluation

Use the [delivery milestones](ROADMAP.md#delivery-milestones) to plan revision work. Develop Balik on the public-archive development corpus, not on friends' drafts. Follow the [development data](ROADMAP.md#development-data) rules and [ADR 0001](docs/adr/0001-public-archive-corpus.md): human-written means dated before 30 November 2022, the license must be recorded for every document, and only commercially licensed text may reach the product. Keep corpus text out of git; commit only the manifest.

During development, compare every candidate with both the basic copyedit and the naive humanizer, and judge changes on the local detector set ([ADR 0002](docs/adr/0002-local-detectors-until-funded.md)). Never report local detector scores as Turnitin or GPTZero results. Record provider results as not measured until milestone 5. Keep each author and every version of their draft on one side of the development/test split. Run reported comparisons on the reference Mac.

Friends take part only at the friends gate (milestone 3). For a beta decision, apply the [blind comparison and beta criteria](ROADMAP.md#blind-comparison-and-beta-criteria) to each language and writing context separately. Report the counts behind each decision and keep reviewer and writer assessments blind to detector scores. Use the [provider reporting rules](ROADMAP.md#how-we-will-evaluate-the-3-target) when describing detector results. Use the terms in [GLOSSARY.md](GLOSSARY.md).

### Issue tracker

Issues and specs live in GitHub Issues for `dodoscoding/Balik-AI-Detector`. See `docs/agents/issue-tracker.md`.

### Triage labels

This repo uses the five default Matt Pocock triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context layout with a root `GLOSSARY.md` and ADRs in `docs/adr/`. See `docs/agents/domain.md`.
