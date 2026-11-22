# Sector addendum: `<name>`

Status: Stub. Copy this file to `sectors/<name>.md`, rename it, and fill every section.

Core method: [`docs/core-methodology.md`](../docs/core-methodology.md). An addendum adds probes and vocabulary only. It cannot remove breakers or dimensions, lower weights, or loosen grade bands.

## 1. Scope
- What businesses count as in scope
- Geography, deal size, and date range for the v0 deal set
- Whether failed, withdrawn and blocked deals are included (they should be)

## 2. Vocabulary for `data/deals.csv`
- `sector`: `<name>`
- `acquirer_type`: list values
- `target_segment`: list values
- Sector-specific columns, if any: define each, with type and notes

## 3. Breaker probes

| Core | <name> probe |
|------|--------------|
| B1 | Which regulators and clearances? |
| B2 | What does customer concentration look like here? |
| B3 | Which ends of life and phase-outs matter? |
| B4 | Which liabilities can exceed deal value? |
| B6 | What makes numbers soft in this sector? |
| B7 | Which certifications and quality gates exist? |
| B9 | What is the critical supply? |
| B10 | Which trade or subsidy conditions are at play? |
| B11 | What is typical catch-up spending here? |

Use the rows you need. Leave unused rows out rather than padding.

## 4. Dimension probes
- **D1.** Rationale candidates in sector wording.
- **D2.** How revenue is booked: contracts, programs, subscriptions, project-based.
- **D3.** Name the sector technology transition.
- **D8.** Which approvals and geopolitical exposures matter here.
- **D9.** Fill only when the sector deviates from the core.

## 5. Maintenance figures
Only when the sector is asset- or warranty-heavy; otherwise delete this section.

## 6. Backtest notes
Findings from grading real deals in this sector go here.
