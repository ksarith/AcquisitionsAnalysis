# Automotive Acquisitions Analysis

A structured way to judge automotive M&A deals: first screen for deal breakers, then score the rest, then grade each deal **Great / Good / Okay / Bad / Horrid**.

## How it works

1. **Gate 1: Deal breakers.** Eleven mandatory questions. Any unmitigated "yes" (or unresolved "unknown") makes the deal Horrid, whatever else it scores.
2. **Gate 2: Scored dimensions.** Nine dimensions, each with mandatory questions, scored 0 to 4.
3. **Grade.** Weighted score converts to a grade band.
4. **Backtest.** Grade closed deals twice: once using only what was known at announcement, once with hindsight. The gap shows whether the questions work.

Full question list and scoring rules: [`docs/methodology.md`](docs/methodology.md)
Field definitions: [`docs/schema.md`](docs/schema.md)
Deal table: [`data/deals.csv`](data/deals.csv)

## Scope (v0)

- Automotive: OEMs, Tier 1/2/3 suppliers, EV/battery, ADAS/software, aftermarket
- North America and Europe, deals over $100M, announced 2020 onward
- Include failed, withdrawn and blocked deals. They teach as much as closed ones.

## Rules

- Every answer needs a source or an explicit "unknown". Unknown is never a pass.
- Do not commit paid-database exports (CapIQ, PitchBook, etc.). Commit only your own derived fields.
- Grades are opinions with evidence, not facts. Record `grade_date` and `grade_basis` every time.

## Status

Early draft. Grade thresholds and weights are starting values and have not been calibrated.
