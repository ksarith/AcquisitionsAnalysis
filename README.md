# DealIntegrity

Two questions about an M&A deal, answered separately and then combined by a hard rule:

1. **Is the deal sound?** (structural integrity) Eleven deal breakers, nine scored dimensions, graded **Great / Good / Okay / Bad / Horrid**.
2. **Was it negotiated with integrity?** (negotiation integrity) Ten dimensions, three failure predicates, classified **Exceptional / High Quality / Competent / Marginal / Poor / Failed**.

The **overall verdict** is the worse of the two. A good deal reached by a deceptive process, or a clean process that produced a fatally flawed deal, cannot hide behind its strong side.

The structural method is carried forward unchanged from AcquisitionsAnalysis (core-0.3). The negotiation layer is new (negotiation-0.1): the idea is Grok's DealIntegrity v0.1.0 draft, rebuilt on the tested core. The method is sector-neutral; sector knowledge lives in **packs**. Automotive is the first pack.

The analyst or agent gathers evidence and answers the questions. **A tool applies the grade rules** and checks the record, so the arithmetic and the precedence are never improvised.

## How it works

1. **Choose the scope** of the assessment: `structural`, `negotiation`, or `both`.
2. **Structural: Gate A** (eleven breakers: any unmitigated "yes" or unresolved "unknown" makes the deal Horrid) then **Gate B** (nine dimensions scored 0 to 4). The grade is the worst of three ceilings: breakers, zero-scored dimensions, score band.
3. **Negotiation: Gate C** (ten dimensions scored 0 to 100, or left blank if unknown). A blank dimension makes the result **Unresolved**, never a pass. A failure predicate (epistemic integrity, risk allocation or procedural legitimacy below 40) makes it **Failed** whatever else it scores.
4. **Overall verdict:** the worse of the in-scope sides, with the side that drove it and a flag if unknowns leave it provisional.
5. **Backtest.** Assess closed deals twice: once with only what was known at the time (`prospective`), once with hindsight (`retrospective`).

Every answer cites evidence. Weights, bands, predicates and the verdict rule never change by pack or by assessor.

## Data

Three tables in `data/`, joined by id (field definitions in [`docs/schema.md`](docs/schema.md)):

| Table | One row per | Holds |
|-------|-------------|-------|
| [`data/deals.csv`](data/deals.csv) | deal | Facts only: parties, status, value, outcome notes |
| [`data/assessments.csv`](data/assessments.csv) | assessment of a deal | Structural answers, negotiation scores, maintenance figures, computed grades. A deal can have several |
| [`data/evidence.csv`](data/evidence.csv) | piece of evidence | Source, date, type, what it establishes, which answer it backs |

Structural and negotiation answers share one assessment row; fields of a side that is out of scope stay blank.

## Check your work

Standard library only (Python 3).

```
python3 tools/calculate_grade.py data/assessments.csv      # recompute grades, scores, verdict
python3 tools/validate_data.py                             # headers, ids, scope, evidence rules, computed fields
python3 -m unittest discover -s tests                      # the tools' own tests
```

Both tools exit 0 when clean, 3 when they find problems, 2 on a usage or input error. A synthetic worked example (an invented deal with a prospective structural assessment, a retrospective one covering both sides, and a negotiation-only one with an unknown) is in [`examples/synthetic/`](examples/synthetic/): run `python3 tools/validate_data.py --data examples/synthetic`. Never copy it into `data/`.

## For agents

[`SKILL.md`](SKILL.md) tells an agent when to use this method, what it needs, how to gather and record evidence, what it must never do, and how to report. [`docs/report_template.md`](docs/report_template.md) is the output format.

## Documents

- Method: [`docs/methodology.md`](docs/methodology.md)
- Field definitions and evidence rules: [`docs/schema.md`](docs/schema.md)
- Packs (how they work, how to add one): [`packs/README.md`](packs/README.md)

## Packs

| Pack | Version | Covers |
|------|---------|--------|
| [`automotive`](packs/automotive/pack.md) | 0.1 | OEMs, Tier 1/2/3 suppliers, EV/battery, ADAS/software, aftermarket |

## Rules

- Every answer needs a source or an explicit "unknown". Unknown is never a pass, and "nothing found" is a finding that needs its own evidence row.
- Do not commit paid-database exports. Commit only your own derived fields and summaries.
- Grades are opinions with evidence, not facts. Record `grade_basis`, `assessment_scope`, `assessment_date` and `method_version` every time.
- `maint_adj_ebitda` is an analytical proxy defined in the methodology, not a standard accounting measure.
- Negotiation conduct is often private. Score only what the record supports; leave the rest blank.

## Status

Early draft (package v0.1.1). A methodology with deterministic checks, not yet a validated predictor. The structural layer (core-0.3) has starting-value thresholds and no real deals assessed. The negotiation layer (negotiation-0.1) is newer: its bands, predicate thresholds, unknown rule and the multiplicative diagnostic are starting values that have not been tried on real negotiations. See [`Disclaimer.md`](Disclaimer.md).
