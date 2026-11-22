# Acquisitions Analysis

A structured way to judge M&A deals in any sector: first screen for deal breakers, then score the rest, then grade each deal **Great / Good / Okay / Bad / Horrid**.

The core method is sector-neutral. Sector knowledge lives in addenda under [`sectors/`](sectors/). The automotive addendum is the first worked example; the framework is broad spectrum by design, with focal points added over time.

## How it works

1. **Gate 1: Deal breakers.** Eleven mandatory questions. Any unmitigated "yes" (or unresolved "unknown") makes the deal Horrid, whatever else it scores.
2. **Gate 2: Scored dimensions.** Nine dimensions, each with mandatory questions, scored 0 to 4.
3. **Grade.** Weighted score converts to a grade band.
4. **Backtest.** Grade closed deals twice: once using only what was known at announcement, once with hindsight. The gap shows whether the questions work.

## Structure

| Path | What it is |
|------|------------|
| [`docs/core-methodology.md`](docs/core-methodology.md) | Sector-neutral question set, scoring, grades, calibration |
| [`docs/schema.md`](docs/schema.md) | Field definitions for the deal table |
| [`data/deals.csv`](data/deals.csv) | One row per deal, all sectors |
| [`sectors/automotive.md`](sectors/automotive.md) | Automotive addendum: sector probes, vocabulary, scope |
| [`sectors/TEMPLATE.md`](sectors/TEMPLATE.md) | Scaffold for adding a new sector track |

## Sector tracks

| Track | Status |
|-------|--------|
| Automotive | Working (first addendum) |
| Software | Planned |
| Healthcare | Planned |
| Energy and infrastructure | Planned |
| Consumer goods | Planned |

A track is Working only when its addendum is written and has been used on at least one real deal. Addenda sharpen questions and add vocabulary; they never weaken or reorder the core gates.

## Rules

- Every answer needs a source or an explicit "unknown". Unknown is never a pass.
- Do not commit paid-database exports (CapIQ, PitchBook, etc.). Commit only your own derived fields.
- Grades are opinions with evidence, not facts. Record `grade_date` and `grade_basis` every time.

## Status

Early draft. Grade thresholds and weights are starting values and have not been calibrated.
