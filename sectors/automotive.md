# Sector addendum: Automotive

Status: Working. First addendum; the core method was built on automotive deals, so this file carries the original sector probes.

Core method: [`docs/core-methodology.md`](../docs/core-methodology.md). This file only adds automotive probes and vocabulary. It cannot weaken the core.

## 1. Scope (v0)

- OEMs, Tier 1/2/3 suppliers, EV/battery, ADAS/software, aftermarket
- North America and Europe, deals over $100M, announced 2020 onward
- Include failed, withdrawn and blocked deals. They teach as much as closed ones.

## 2. Vocabulary for `data/deals.csv`

- `sector`: `automotive`
- `acquirer_type`: `oem`, `tier1`, `tier2`, `pe`, `tech`, `other`
- `target_segment`: `powertrain`, `ev_battery`, `adas_software`, `chassis`, `interior`, `electronics`, `thermal`, `aftermarket`, `other`

## 3. Breaker probes

| Core | Automotive probe |
|------|------------------|
| B1 | Check antitrust, CFIUS or equivalent, EU merger control, China SAMR, FDI screening. |
| B2 | Does one OEM customer exceed ~40% of revenue, with that business at risk or tied to a platform ending within the hold period? Revenue can vanish on a sourcing decision. |
| B3 | Is majority revenue tied to products or platforms with a known end of production or regulatory phase-out (emissions rules, EV transition) inside ~5 years, with no funded transition? |
| B4 | Recalls, warranty, product liability, environmental legacy, underfunded pensions. Automotive liabilities can exceed deal value and surface years later. |
| B6 | Automotive backlogs are often soft. Unverified numbers mean the thesis is unsupported. |
| B7 | IATF 16949 lapse or risk, OEM probation, controlled shipping, major recall history. Quality status gates future OEM awards. |
| B9 | Core IP, licenses, or critical supply: chips, cells, rare earths. Check change-of-control clauses and export controls. |
| B10 | Tariffs, EV credits, local content rules. Policy risk gets priced as if it were permanent. |
| B11 | Deferred plant maintenance, tooling replacement, mandated retrofits (emissions, safety). |

Breakers B5 and B8 need no sector-specific probe beyond the core.

## 4. Dimension probes

- **D1.** Rationale candidates, sector wording: scale, technology, customer access, vertical integration, geography, defensive.
- **D2.** Program-based revenue: awarded programs, contract lengths, volume guarantees, exposure to OEM sourcing decisions. Aftermarket revenue is the recurring share.
- **D3.** The sector transition is powertrain and software: EV, hybrid, ICE, ADAS, software-defined vehicle. Argue where the target sits on each.
- **D8.** Approvals: EU merger control, CFIUS, China SAMR. Geopolitics: tariffs, export controls, China-specific restrictions, national-security sensitivity of jobs and flagship brands.
- **D9.** Sector upkeep checks: maintenance versus growth capex on plants; age of presses, lines and tooling; mandated retrofits; warranty trend and reserves; serviceability of sealed modules and battery packs; parts-supply, software-update and legacy-platform commitments.

## 5. Maintenance figures

Automotive targets are asset- and warranty-heavy, so the maintenance-adjusted figures in core methodology section 3a matter most here. Fill the maintenance block in `data/deals.csv` for every automotive row; if you cannot, `maint_basis` is `unknown` and D9 is capped at 2.

## 6. Backtest notes

Start the automotive backtest cohort at 20 or more closed deals graded prospectively. Findings from grading real deals are recorded here, not in the core file.
