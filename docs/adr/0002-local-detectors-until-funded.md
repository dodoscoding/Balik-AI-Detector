# Develop against a local detector set; provider targets wait for funding

The product target is 3% or less on Turnitin and GPTZero. Turnitin offers no public API for AI-writing detection. GPTZero's API is paid, and its site terms forbid automated use. The project has no budget. Development therefore uses a local detector set on the reference machine: at least two zero-shot detectors and one classifier trained on permissively licensed human-vs-AI data. A change must improve scores on at least two detectors, so Balik is never tuned to a single detector. Provider results are recorded as not measured until milestone 5. That milestone needs funding and each provider's written permission for this use.

## Consequences

- Local detector scores never stand in for Turnitin or GPTZero results in reports, in the product, or in claims.
- The 3% target stays in the roadmap as an unmeasured provider target.
- A provider may refuse benchmarking for a tool that revises AI drafts. Turnitin markets detection of bypasser tools. If a provider refuses, that provider stays not measured, and Balik makes no claim about it.
- Turnitin's AI writing detection may not support Turkish. Confirm its language scope before planning any Turkish target.
