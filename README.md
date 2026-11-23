# DealIntegrity

A structured way to judge M&A deals: whether the deal itself is sound, and whether it was negotiated with integrity. Two separate axes, combined by a worst-of rule, so excellence on one side can never paper over failure on the other. The core is sector-neutral; sector knowledge lives in packs. Broad spectrum by design, with focal points added over time.

## The two axes

- **Structural integrity** (core-0.3): Gate A, eleven deal breakers (B1 to B11); Gate B, nine scored dimensions (D1 to D9). Grade: Great / Good / Okay / Bad / Horrid. Any unmitigated breaker is Horrid whatever the score, and a documented mitigation caps the verdict at Okay.
- **Negotiation integrity** (negotiation-0.1, new, uncalibrated): Gate C, ten dimensions (N1 to N10, scored 0 to 100) and three failure predicates (F1 to F3), classified Exceptional down to Failed. Dimensions the record cannot support stay blank, and the negotiation is then Unresolved; unknown is never a pass.
- **Overall verdict:** the worse of the sides in scope, on one shared scale. Unresolved unknowns mark a verdict provisional.

## How an assessment runs

1. One row in `data/deals.csv` for the deal facts.
2. Evidence first: every answer and every score cites a row in `data/evidence.csv`. A prospective assessment carries an `information_cutoff`; the validator rejects evidence dated after it. "Nothing found" is recorded as a `negative_finding`.
3. Answers and scores in `data/assessments.csv`: breakers `Y`/`N`/`U`/`M`, structural dimensions 0 to 4, negotiation dimensions 0 to 100 or blank.
4. `python3 tools/calculate_grade.py data/assessments.csv` then `python3 tools/validate_data.py`. The agent judges; the tool computes. Computed fields are never hand-edited.
5. Report with `docs/report_template.md`.

`SKILL.md` is the full agent skill. A worked synthetic example with expected results is in `examples/synthetic/`.

## Structure

| Path | What it is |
|------|------------|
| [`SKILL.md`](SKILL.md) | The agent skill: inputs, workflow, hard rules |
| [`docs/methodology.md`](docs/methodology.md) | The method: core-0.3 plus negotiation-0.1, with the change log |
| [`docs/schema.md`](docs/schema.md) | The three data tables: deals, assessments, evidence |
| [`docs/report_template.md`](docs/report_template.md) | Report format |
| [`docs/references.md`](docs/references.md) | Outside reading and candidate improvements (not enacted) |
| [`packs/README.md`](packs/README.md) | Pack rules: what a pack may and may not do |
| [`packs/automotive/pack.md`](packs/automotive/pack.md) | Automotive pack v0.1 |
| [`tools/calculate_grade.py`](tools/calculate_grade.py) | Applies the grade rules |
| [`tools/validate_data.py`](tools/validate_data.py) | Checks the tables and the evidence rules |
| [`tests/`](tests/) | Tool and documentation tests |
| [`examples/synthetic/`](examples/synthetic/) | Synthetic worked example, not a real deal |
| [`data/`](data/) | Live tables (empty at v0.1.1: no real deal graded yet) |

## Sector packs

| Pack | Status |
|------|--------|
| `general` | Core only; default when no pack applies |
| `automotive` | Working, v0.1 (extraction from the original automotive method) |
| `software`, `healthcare`, `energy`, `consumer` | Planned |

A pack becomes Working when its pack.md exists and it has been used on at least one real assessment. Packs sharpen wording and may add breakers; they never change weights, bands, predicates or the overall-verdict rule.

## Rules

- Every answer needs a source or an explicit `U`. Unknown is never a pass.
- Do not commit paid-database exports (CapIQ, PitchBook, etc.). Commit only your own derived fields and claims in your own words.
- Grades are opinions with evidence, not facts. Every assessment records `grade_basis`, `grade_perspective`, `assessment_date` and `method_version`.
- No investment advice: the verdict is an opinion on deal quality and negotiation conduct, with cited evidence. See `Disclaimer.md`.

## Status

- Package version v0.1.1. The structural core is carried forward uncalibrated; the negotiation layer and every band and threshold are starting values.
- Next intended steps: a first real assessment through the skill, then the 20-deal per-pack backtest that calibration requires (methodology, section 7).
- History: this repository was AcquisitionsAnalysis, first an automotive-only rubric (v0, v0.1), then a sector-neutral core with addenda (v0.2). Core-0.3 rebuilt the grade rule as worst-of-three-ceilings and split the data model into deals, assessments and evidence. Package v0.1.1 added Gate C (negotiation integrity, adapted from the DealIntegrity v0.1.0 draft with every deviation recorded) and renamed the package. Renamed paths from the earlier layouts (`sectors/`, `docs/core-methodology.md`, wide `deals.csv`) have been retired.
