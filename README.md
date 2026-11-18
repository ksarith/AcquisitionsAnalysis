# Acquisitions Analysis

A structured way to judge M&A deals in any sector: first screen for deal breakers, then score the rest, then grade each deal **Great / Good / Okay / Bad / Horrid**.

The core method is sector-neutral. Sector knowledge lives in **packs** (specializations) that sharpen the core questions for one industry. Automotive is the first pack. A deal can also be graded with the core alone.

The analyst or agent gathers evidence and answers the questions. **A tool applies the grade rules** and checks the record, so the arithmetic and the precedence are never improvised.

## How it works

1. **Gate 1: Deal breakers.** Eleven mandatory questions. Any unmitigated "yes" (or unresolved "unknown") makes the deal Horrid, whatever else it scores.
2. **Gate 2: Scored dimensions.** Nine dimensions, each with mandatory questions, scored 0 to 4.
3. **Grade.** The worst of three ceilings (breakers, zero-scored dimensions, score band).
4. **Backtest.** Assess closed deals twice: once using only what was known at announcement (`prospective`), once with hindsight (`retrospective`). The gap shows whether the questions work.

If the deal's sector has a pack, answer the core questions *as sharpened by the pack*. The weights, bands and grade rule never change by pack, so grades stay comparable across sectors.

## Data

Three tables in `data/`, joined by id (field definitions in [`docs/schema.md`](docs/schema.md)):

| Table | One row per | Holds |
|-------|-------------|-------|
| [`data/deals.csv`](data/deals.csv) | deal | Facts only: parties, status, value, outcome notes |
| [`data/assessments.csv`](data/assessments.csv) | grading of a deal | Breaker answers, dimension scores, maintenance figures, computed grade. A deal can have several |
| [`data/evidence.csv`](data/evidence.csv) | piece of evidence | Source, date, what it establishes, and which answer it backs |

## Check your work

Standard library only (Python 3).

```
python3 tools/calculate_grade.py data/assessments.csv      # recompute grades and maintenance figures
python3 tools/validate_data.py                             # headers, ids, evidence rules, computed fields
python3 -m unittest discover -s tests                      # the tool's own tests
```

Both tools exit 0 when clean, 3 when they find problems, 2 on a usage or input error. A synthetic worked example (invented deal, prospective and retrospective assessments) is in [`examples/synthetic/`](examples/synthetic/): run the tools on it with `--data examples/synthetic` or by passing its `assessments.csv`. Never copy it into `data/`.

## Documents

- Core questions, scoring and grade rules: [`docs/methodology.md`](docs/methodology.md)
- Field definitions and evidence rules: [`docs/schema.md`](docs/schema.md)
- Packs (how they work, how to add one): [`packs/README.md`](packs/README.md)

## Packs

| Pack | Version | Covers |
|------|---------|--------|
| [`automotive`](packs/automotive/pack.md) | 0.1 | OEMs, Tier 1/2/3 suppliers, EV/battery, ADAS/software, aftermarket |

## Scope

- The core has no sector, size, region or date limit of its own. A pack sets the scope for deals graded with it.
- Include failed, withdrawn and blocked deals. They teach as much as closed ones.

## Rules

- Every answer needs a source or an explicit "unknown". Unknown is never a pass, and "nothing found" is a finding that needs its own evidence row.
- Do not commit paid-database exports (CapIQ, PitchBook, etc.). Commit only your own derived fields and summaries.
- Grades are opinions with evidence, not facts. Record `grade_basis`, `assessment_date` and `method_version` every time.
- `maint_adj_ebitda` is an analytical proxy defined in the methodology, not a standard accounting measure.

## Status

Early draft (v0.3). It is a methodology with deterministic checks, not yet a validated predictor. Grade thresholds and weights are starting values and have not been calibrated; no real deals have been assessed. v0.3 fixed a grading inversion, added the three-table data model, the evidence rules and the tools. It changed no weight, band boundary or question.
