# Core Methodology

Sector-specific probes live in `sectors/<name>.md`. This file defines the shared method: breakers, dimensions, scoring and grades. A sector addendum may sharpen the questions and add vocabulary. It may not remove breakers or dimensions, lower their weights, or loosen a grade band.

## 1. Principles

- **Questions before numbers.** The questions are the product. Scores summarize the answers.
- **Evidence or unknown.** Each answer is `Y`, `N`, or `U` (unknown), plus a source. `U` is treated as a risk until resolved.
- **Two grading modes.** `prospective` uses only information available at announcement. `retrospective` uses hindsight. Never mix them in one grade.
- **Perspective matters.** Grade from the acquirer point of view unless `grade_perspective` says otherwise. A great deal for sellers can be a horrid deal for buyers.
- **Core is additive-only for sectors.** Addenda add probes and vocabulary. They never delete a question or change a gate rule.

## 2. Gate 1: Deal breakers (mandatory)

Answer every question. Any `Y` or `U` is an **unmitigated breaker** unless a specific mitigation is documented with a source.

| ID | Question | Why it kills deals |
|----|----------|--------------------|
| B1 | Is there a credible path to regulatory clearance (antitrust, merger control, FDI screening, sector regulators)? Answer `Y` here means **no** credible path. | Blocked or abandoned deals cost time, fees and focus. |
| B2 | Does one customer exceed ~40% of target revenue, with that business at risk or tied to a contract, program or platform ending within the hold period? | Revenue can vanish on a sourcing decision. |
| B3 | Is a majority of target revenue tied to products or platforms with a known end of life or regulatory phase-out inside ~5 years, with no funded transition? | A declining base is bought at a growth price. |
| B4 | Are there unquantified or uncapped liabilities: warranty, product liability, environmental legacy, underfunded pensions, open litigation? | Liabilities can exceed deal value and surface years later. |
| B5 | Can the acquirer fund the deal and the integration without breaching covenants, losing its credit rating tier, or relying on assets it must sell at a bad time? | Financing stress turns a good asset into a bad deal. |
| B6 | Are the target key numbers (revenue, margin, backlog, order book) unverified by audited filings or credible diligence? | Backlogs are often soft. Unverified means the thesis is unsupported. |
| B7 | Is the target quality or delivery standing at risk: key certifications lapsed or lost, major-customer probation, controlled shipments, major recall history? | Quality status gates future awards. |
| B8 | Does a labor, union, works council, or government agreement block the site, headcount or footprint changes the synergy case needs? | The synergy case may be legally unreachable. |
| B9 | Is ownership of core IP, licenses, or critical supply unclear, contingent on a change-of-control clause, or exposed to export controls? | Buyer may not get what it thinks it is buying. |
| B10 | Does the deal depend on trade or subsidy conditions (tariffs, subsidies, local content rules) that could reverse and have no pass-through or fallback? | Policy risk gets priced as if it were permanent. |
| B11 | Does the asset base need catch-up spending (deferred maintenance, tooling replacement, mandated retrofits) above roughly 1x annual EBITDA, with no price adjustment? | EBITDA flatters the target until the bill arrives. |

**Rule:** any unmitigated breaker means the verdict is **Horrid / Pass**, regardless of score. A documented mitigation caps the verdict at **Okay**.

Record per breaker: `Y`, `N`, `U`, or `M` (mitigated, with note).

## 3. Gate 2: Scored dimensions

Answer the questions, then score each dimension **0 to 4**.

Anchors: **0** serious problem, **1** weak, **2** average or neutral, **3** good, **4** clearly strong with evidence.

### D1. Strategic fit and rationale (weight 2)
- What specific problem does this solve or what capability does it add? Could the buyer build or partner instead, more cheaply?
- Is the rationale one of: scale, technology, customer access, vertical integration, geography, defensive? Is it stated with numbers?
- Does the deal fit the acquirer track record, or is it a stretch into an unfamiliar segment?
- Would the deal still make sense at a 20% higher price?

### D2. Customer and contract quality (weight 2)
- Customer mix: how many customers, what share per customer, and how stable is each relationship?
- Is revenue booked (awarded contracts, contract length, volume guarantees) or hoped for?
- Does the target have pricing power or pass-through for input cost inflation?
- How much revenue is recurring or aftermarket versus one-time or project-based?

### D3. Technology and cycle timing (weight 2)
- Is the product position on the right side of the technology transition in this sector? Name the transition and argue the position. The sector addendum lists what it is.
- Is the technology proven in production, or demo stage? Who else is close?
- Is the deal timed at a cycle peak (high multiples, strong volumes) or trough?
- Does the target depend on a single technology bet?

### D4. Financial quality (weight 2)
- Margin trend over 3+ years: stable, rising, falling? Compared with segment peers?
- Cash conversion and capex intensity: is EBITDA real cash?
- Capacity utilization and fixed-cost leverage: what happens to margin if volume drops 15%?
- Debt, leases, and off-balance-sheet obligations assumed?
- How much of reported EBITDA survives after maintenance spending? (See D9 and section 3a.)

### D5. Price and structure (weight 2)
- Multiple paid versus segment comps and the target own history. Is `value_basis` disclosed, reported or estimated?
- How much of the price is paid for synergies the seller created none of?
- Structure: earn-outs, escrow, price adjustments, reverse break fees, financing conditions. Who carries the risk?
- Does the price work if synergies come in at half the plan?
- Is the multiple quoted on plain or maintenance-adjusted figures?

### D6. Synergy credibility (weight 1)
- Are synergies quantified, split into cost versus revenue, and phased by year?
- Which cost synergies need site closures or layoffs, and are those feasible under B8?
- Do revenue synergies depend on customers behaving differently? (Treat as low confidence.)
- Does the acquirer have a history of delivering announced synergies?

### D7. Integration and people (weight 1)
- Who runs the target after close? Are key people retained or locked in?
- Culture, systems and footprint overlap: how many sites, ERPs, and product lines must merge?
- Is the acquirer doing other large integrations at the same time?
- Is there a clear first-100-days plan?

### D8. Regulatory and geopolitical exposure (weight 1)
- Which approvals are needed, how long, and with what likely remedies (divestitures, behavioral conditions)?
- Exposure to tariffs, sanctions, export controls, or jurisdiction-specific restrictions?
- Are there national-security or local political sensitivities (jobs, flagship brands, strategic tech)?
- Timeline risk: could delays outlast financing commitments?

### D9. Maintenance and lifecycle burden (weight 2)

Covers both the upkeep of what the target owns (facilities, equipment, tooling) and the upkeep of what it sells (warranty, service, parts, support). Known upcoming costs go into the figures, not into a footnote.

- **Maintenance vs. growth capex:** what does it cost per year just to keep current output running, separate from expansion? Is the target spending that much now?
- **Asset age and deferred work:** average age of facilities and equipment. What overhauls, rebuilds or replacements are scheduled or overdue in the next 5 years, and what do they cost?
- **Compliance retrofits:** are environmental, safety or other rules coming that force site or product changes?
- **Warranty, service and repair cost:** warranty or service expense as a percent of revenue, its 3-year trend, and whether reserves cover claims still open.
- **Serviceability of the product:** how costly and hard is it to repair (design choices, special tools, labor hours, parts availability)? Does that cost fall on the target, the customer, or a third party?
- **Support tail:** parts-supply, update and legacy-platform commitments, and how many years they run.
- **In the numbers:** is the multiple computed on maintenance-adjusted figures (see section 3a), and has the known upcoming cost been taken out of the price?

## 3a. Maintenance-adjusted figures

Record the plain figures and the adjusted ones side by side. Plain EBITDA overstates what a buyer can take out of a business that needs upkeep.

```
maint_adj_ebitda   = EBITDA - maintenance_capex - warranty_normalization
                     (warranty_normalization = normalized annual warranty cost minus
                      what is already expensed, if positive)
maint_adj_ev_ebitda = enterprise_value / maint_adj_ebitda
price_adj_for_known = enterprise_value - known_upcoming_costs
                     (catch-up capex, scheduled overhauls, mandated retrofits,
                      open warranty claims not reserved; 5-year horizon)
```

Rules:
- Use the buyer best estimate and say how it was derived. Mark estimates as estimates.
- If maintenance capex is unknown, record it as unknown and score D9 no higher than 2.
- Compare maintenance-adjusted multiples with each other, not with plain multiples.

## 4. Computing the grade

```
weighted_score = sum(dimension_score x weight)
max_score      = 4 x sum(weights)   # 4 x 15 = 60
score_pct      = weighted_score / max_score
```

| Grade | Condition (starting values, uncalibrated) |
|-------|-------------------------------------------|
| **Great** | score_pct >= 80%, no breakers (`Y`, `U`, or `M`), no dimension scored 0 |
| **Good** | score_pct 65 to 79%, no unmitigated breakers, no dimension scored 0 |
| **Okay** | score_pct 50 to 64%, or any grade capped by a mitigated breaker |
| **Bad** | score_pct 35 to 49%, or any dimension scored 0 |
| **Horrid** | score_pct < 35%, or any unmitigated breaker |

Order of checks: breakers first, then zero-scored dimensions, then percentage.

## 5. Calibration (backtesting)

1. Grade 20 or more closed deals prospectively, using only announcement-time information. Backtest each sector track on its own deals.
2. Record outcomes 3+ years later in `outcome_grade` and `outcome_notes` (value created or destroyed, impairments, divestitures, integration problems).
3. Compare. If "Good" deals regularly end badly, find which question failed to catch the problem and add or sharpen it.
4. Revise thresholds and weights only after backtesting, and log each change below.

## 6. Adding a sector track

- Copy `sectors/TEMPLATE.md` to `sectors/<name>.md` and fill it in.
- Define the segment and acquirer vocabularies for the schema.
- Add sector probes per breaker and dimension where this sector deviates from the core.
- Update the track table in the README. Status `Working` needs at least one real deal graded with the addendum.

## 7. Change log

- v0: initial question set, weights and bands (unvalidated). Scope: automotive only.
- v0.1: added D9 (maintenance and lifecycle burden, weight 2), breaker B11 (catch-up spending), maintenance-adjusted figures (3a). Max score now 60.
- v0.2: restructured around a sector-neutral core. Automotive specifics moved to `sectors/automotive.md`; `sector` column added to the deal table; addendum template added; core is additive-only for sectors.
