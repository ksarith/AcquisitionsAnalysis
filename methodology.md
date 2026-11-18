# Methodology (core)

This is the sector-neutral core. A sector's specialization lives in a pack (see [`../packs/README.md`](../packs/README.md)). Where a core question has a sector reading, the pack shows the original wording beside it.

## 1. Principles

- **Questions before numbers.** The questions are the product. Scores summarize the answers.
- **Evidence or unknown.** Each answer is `Y`, `N`, or `U` (unknown). Every answer except `U` is backed by at least one evidence row (see [`schema.md`](schema.md)). `N` is a finding, not a default: "nothing found" needs a row saying what was searched and where. `U` is treated as a risk until resolved.
- **Two grading modes.** `prospective` uses only information available at announcement. `retrospective` uses hindsight. Never mix them in one assessment: a prospective assessment carries an `information_cutoff` and the checker rejects evidence dated after it. A deal can have many assessments; they never overwrite each other.
- **Perspective matters.** Grade from the acquirer's point of view unless `grade_perspective` says otherwise. A great deal for sellers can be a horrid deal for buyers.
- **The agent judges; the tool computes.** Gathering evidence and answering the questions is judgment. Applying the grade rules and the maintenance formulas is mechanical and is done by [`../tools/calculate_grade.py`](../tools/calculate_grade.py), never improvised. Recorded computed fields are checked against it by [`../tools/validate_data.py`](../tools/validate_data.py).
- **Core first, pack second.** Answer the core question, reading it through the sector's pack when one applies. Weights and bands are the core's and do not vary by pack.

## 2. Gate 1: Deal breakers (mandatory)

Answer every question. Any `Y` or `U` is an **unmitigated breaker** unless a specific mitigation is documented with a source.

| ID | Question | Why it kills deals |
|----|----------|--------------------|
| B1 | Is there a credible path to regulatory clearance (antitrust, CFIUS or equivalent, EU merger control, China SAMR, FDI screening)? Answer `Y` here means **no** credible path. | Blocked or abandoned deals cost time, fees and focus. |
| B2 | Does one customer (or one tightly linked customer group) exceed ~40% of target revenue, with that business at risk or tied to a contract or platform ending within the hold period? | Revenue can vanish on a sourcing decision. |
| B3 | Is a majority of target revenue tied to products, platforms or markets with a known end of life or regulatory phase-out inside ~5 years, with no funded transition? | Declining base is bought at a growth price. |
| B4 | Are there unquantified or uncapped liabilities: recalls, warranty, product liability, environmental legacy, underfunded pensions? | Liabilities can exceed deal value and surface years later. |
| B5 | Can the acquirer fund the deal and the integration without breaching covenants, losing its credit rating tier, or relying on assets it must sell at a bad time? | Financing stress turns a good asset into a bad deal. |
| B6 | Are the target's key numbers (revenue, margin, backlog, order book) unverified by audited filings or credible diligence? | Backlogs and pipelines are often soft. Unverified means the thesis is unsupported. |
| B7 | Is the target's quality, certification or licence-to-operate standing at risk (certification lapse, customer probation, regulator action, major recall history)? | Standing gates future awards and the right to operate. |
| B8 | Does a labor, union, works council, or government agreement block the plant, headcount or footprint changes the synergy case needs? | The synergy case may be legally unreachable. |
| B9 | Is ownership of core IP, licenses, or critical supply (key components or materials) unclear, contingent on a change-of-control clause, or exposed to export controls? | Buyer may not get what it thinks it is buying. |
| B10 | Does the deal depend on trade or subsidy conditions (tariffs, tax credits, local content rules) that could reverse and have no pass-through or fallback? | Policy risk gets priced as if it were permanent. |
| B11 | Does the asset base need catch-up spending (deferred plant maintenance, tooling replacement, mandated retrofits) above roughly 1x annual EBITDA, with no price adjustment? | EBITDA flatters the target until the bill arrives. |

**Rule:** any unmitigated breaker means the verdict is **Horrid / Pass**, regardless of score. A documented mitigation caps the verdict at **Okay**. This includes any breaker a pack adds.

Record per breaker: `Y`, `N`, `U`, or `M` (mitigated, with note).

## 3. Gate 2: Scored dimensions

Answer the questions, then score each dimension **0 to 4**.

Anchors: **0** serious problem, **1** weak, **2** average or neutral, **3** good, **4** clearly strong with evidence.

### D1. Strategic fit and rationale (weight 2)
- What specific problem does this solve or what capability does it add? Could the buyer build or partner instead, more cheaply?
- Is the rationale one of: scale, technology, customer access, vertical integration, geography, defensive? Is it stated with numbers?
- Does the deal fit the acquirer's track record, or is it a stretch into an unfamiliar segment?
- Would the deal still make sense at a 20% higher price?

### D2. Customer and contract quality (weight 2)
- Customer mix: how many customers, what share per customer, and how stable is each relationship?
- Is revenue booked (awarded programs, contract length, volume guarantees) or hoped for?
- Does the target have pricing power or pass-through for raw materials, energy and labor?
- How much revenue is recurring (aftermarket, service, subscription) versus one-off or program-based?

### D3. Technology and cycle timing (weight 2)
- Is the product position on the right side of the technology or market transition that matters in this sector?
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
- Multiple paid versus segment comps and the target's own history. Is `value_basis` disclosed, reported or estimated?
- How much of the price is paid for synergies the seller created none of?
- Structure: earn-outs, escrow, price adjustments, reverse break fees, financing conditions. Who carries the risk?
- Does the price work if synergies come in at half the plan?
- Is the multiple quoted on plain or maintenance-adjusted figures?

### D6. Synergy credibility (weight 1)
- Are synergies quantified, split into cost versus revenue, and phased by year?
- Which cost synergies need plant closures or layoffs, and are those feasible under B8?
- Do revenue synergies depend on customers behaving differently? (Treat as low confidence.)
- Does the acquirer have a history of delivering announced synergies?

### D7. Integration and people (weight 1)
- Who runs the target after close? Are key engineers and executives retained or locked in?
- Culture, systems and footprint overlap: how many plants, ERPs, and product lines must merge?
- Is the acquirer doing other large integrations at the same time?
- Is there a clear first-100-days plan?

### D8. Regulatory and geopolitical exposure (weight 1)
- Which approvals are needed, how long, and with what likely remedies (divestitures, behavioral conditions)?
- Exposure to tariffs, sanctions, export controls, or China-specific restrictions?
- Are there national-security or local political sensitivities (jobs, flagship brands, strategic tech)?
- Timeline risk: could delays outlast financing commitments?

### D9. Maintenance and lifecycle burden (weight 2)

Covers both the target's own upkeep (plants, tooling, equipment) and the upkeep of what it sells (warranty, repair, parts, support). Known upcoming costs go into the figures, not into a footnote.

- **Maintenance vs. growth capex:** what does it cost per year just to keep current output running, separate from expansion? Is the target spending that much now?
- **Asset age and deferred work:** average age of plant, equipment, tooling and systems. What overhauls, rebuilds or replacements are scheduled or overdue in the next 5 years, and what do they cost?
- **Compliance retrofits:** are emissions, safety or environmental rules coming that force plant or product changes?
- **Warranty and repair cost:** warranty expense as a percent of revenue, its 3-year trend, and whether reserves cover claims still open.
- **Serviceability of the product:** how costly and hard is it to repair (modularity, special tools, labor hours, parts availability)? Does that cost fall on the target, the customer, or the maker?
- **Support tail:** parts-supply, software-update and legacy-platform commitments, and how many years they run.
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
- Use the buyer's best estimate and say how it was derived (in `maint_notes`). Mark estimates as estimates.
- If maintenance capex is unknown, record it as unknown and score D9 no higher than 2. Any blank input leaves the computed figure blank (unknown); nothing is filled in by assumption.
- Compare maintenance-adjusted multiples with each other, not with plain multiples.
- **Not a standard measure.** `maint_adj_ebitda` is an analytical proxy defined here, not an accounting or reported measure. Say so wherever it is quoted.
- **Annual vs one-time.** `maint_capex` and `warranty_normalization` are annual and recurring; they reduce EBITDA. `catchup_capex` and the other known upcoming costs are one-time; they reduce price. Do not subtract a cost in both places.
- **Overlap.** `known_upcoming_costs` includes `catchup_capex`, so it can never be smaller than it. The checker enforces this.
- **Horizon and discounting (starting rule).** `known_upcoming_costs` is the undiscounted nominal sum over a 5-year horizon. If a discounted figure is used, say so in `maint_notes` and use it consistently.
- **Non-positive adjusted EBITDA (starting rule).** If `maint_adj_ebitda` is zero or negative, upkeep consumes the earnings: the multiple is not meaningful and is left blank, D4 may not be scored above 1, and `maint_notes` must explain. D9 is scored on its own questions.
- `price_adj_for_known` is recorded in `price_adj_for_known_usd_m`, and the adjusted EBITDA in `maint_adj_ebitda_usd_m`; both are computed by the tool.

## 4. Computing the grade

```
weighted_score = sum(dimension_score x weight)
max_score      = 4 x sum(weights)   # 4 x 15 = 60
score_pct      = weighted_score / max_score
```

The grade is the **worst** of three independent ceilings. Each is computed on its own, then the lowest wins. There is no order of checks to get wrong.

| Ceiling | Result |
|---------|--------|
| **Breaker ceiling** | Any core `Y` or `U`, or pack breakers `unmitigated` -> **Horrid**. Otherwise any core `M`, or pack breakers `mitigated` -> **Okay**. Otherwise no ceiling. |
| **Zero-dimension ceiling** | Any dimension scored 0 -> **Bad**. Otherwise no ceiling. |
| **Score band** | See below. |

| Score band | Weighted score (of 60) | Starting values, uncalibrated |
|------------|------------------------|-------------------------------|
| **Great** | 48 or more (80%+) | |
| **Good** | 39 to 47 (65% to under 80%) | |
| **Okay** | 30 to 38 (50% to under 65%) | |
| **Bad** | 21 to 29 (35% to under 50%) | |
| **Horrid** | 20 or less (under 35%) | |

Bands use whole weighted-score points, so there is no rounding at the edges.

Examples: all dimensions 4 with one `M` breaker is **Okay** (breaker ceiling). All dimensions 4 with one dimension at 0 is **Bad** (zero-dimension ceiling). Every dimension at 0 is **Horrid** (score band). A deal can never grade better for scoring worse.

*Why this changed in v0.3:* v0.2 and earlier checked breakers, then zero-scored dimensions, then percentage, first match winning. That graded a 0% deal with a zero dimension **Bad**, but a 20% deal with none **Horrid**. The worst-of rule fixes the inversion and gives the same grade as the old table everywhere else.

## 5. Packs

A pack sharpens the core for one sector. It may define scope, field values, sector readings of core questions, extra prompts and extra breakers. It may not change weights, bands, the order of checks or the unknown rule. Rules and the template are in [`../packs/README.md`](../packs/README.md).

Record `sector` (the pack id, or `general`) on the deal and `method_version` (core and pack versions) on every assessment, so a grade can be reproduced.

## 6. Calibration (backtesting)

1. Grade 20 or more closed deals prospectively, using only announcement-time information (one `prospective` assessment each).
2. Record outcomes 3+ years later in the deal's `outcome_notes` (value created or destroyed, impairments, divestitures, integration problems) and add a `retrospective` assessment of the same deal.
3. Compare the two assessments. If "Good" deals regularly end badly, find which question failed to catch the problem and add or sharpen it.
4. Revise thresholds and weights only after backtesting, and log each change below.
5. Backtest **per pack** (20 or more deals in the sector) before changing that pack's readings or thresholds. A change to the core needs a pooled backtest across sectors; until deals from more than one sector exist, core changes are provisional.

## 7. Change log

- v0: initial question set, weights and bands (unvalidated).
- v0.1: added D9 (maintenance and lifecycle burden, weight 2), breaker B11 (catch-up spending), maintenance-adjusted figures (3a). Max score now 60.
- v0.2: restructured into a sector-neutral core plus packs. Automotive moved to [`../packs/automotive/pack.md`](../packs/automotive/pack.md) as the first pack. **No weight, band or threshold changed**; the max score is still 60. Question numbering (B1 to B11, D1 to D9) is unchanged. Wording was generalized where it named automotive terms; the original wording is kept verbatim in the automotive pack. Section 5 (packs) added; calibration renumbered to 6 and extended per pack.
- v0.3: **grade rule** replaced by worst-of-three-ceilings (fixes an inversion in the v0.2 table); **maintenance figures** specified further (non-standard-measure note, annual vs one-time, overlap, horizon and discounting, non-positive adjusted EBITDA) and `maint_adj_ebitda_usd_m` and `price_adj_for_known_usd_m` added to the schema; **data model** split into `deals`, `assessments` and `evidence` so one deal carries several assessments and every answer cites evidence; **evidence rule** tightened (`N` needs a supporting row; the earlier "answer N and say why" path for non-applicable questions is gone); added `tools/calculate_grade.py`, `tools/validate_data.py`, tests and a synthetic worked example. **No weight, band boundary or question changed.** The two non-positive-EBITDA rules and the evidence-row requirement are starting values, uncalibrated.
