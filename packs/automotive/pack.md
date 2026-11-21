# Automotive pack (v0.1)

The automotive specialization of the DealIntegrity core ([`../../docs/methodology.md`](../../docs/methodology.md)). Version 0.1 is an **extraction**: everything automotive-specific in the earlier all-automotive method (core v0.1) moved here unchanged, so deals graded under that version keep the same meaning. Weights, bands and thresholds are the core's.

## 1. Scope

- Automotive: OEMs, Tier 1/2/3 suppliers, EV/battery, ADAS/software, aftermarket
- North America and Europe, deals over $100M, announced 2020 onward
- Include failed, withdrawn and blocked deals. They teach as much as closed ones.

These limits were the package's v0 scope; they are now this pack's scope, not the core's. Loosening them is a pack change, logged below.

## 2. Field values

Set `sector` to `automotive`.

| Field | Allowed values |
|-------|----------------|
| `subsector` | `powertrain`, `ev_battery`, `adas_software`, `chassis`, `interior`, `electronics`, `thermal`, `aftermarket`, `other` |
| `acquirer_role` | `oem`, `tier1`, `tier2`, `pe`, `tech`, `other` |

Mapping from the earlier schema: `target_segment` is now `subsector` (same values); `acquirer_type` is now core `acquirer_type` (`strategic` for `oem`, `tier1`, `tier2` and `tech`; `pe` for `pe`; `other` for `other`) plus `acquirer_role` (the earlier value, unchanged).

## 3. Breaker readings

Each reading is the **original wording** of the core question as written for automotive in core v0.1. Answer the core question using this reading for automotive deals.

**B2.** Does one customer (usually one OEM) exceed ~40% of target revenue, with that business at risk or tied to a platform ending within the hold period?
*Why it kills deals (automotive reading):* Revenue can vanish on a sourcing decision.

**B3.** Is a majority of target revenue tied to products or platforms with a known end of production or regulatory phase-out inside ~5 years, with no funded transition?
*Why it kills deals (automotive reading):* Declining base is bought at a growth price.

**B4.** Are there unquantified or uncapped liabilities: recalls, warranty, product liability, environmental legacy, underfunded pensions?
*Why it kills deals (automotive reading):* Auto liabilities can exceed deal value and surface years later.

**B6.** Are the target's key numbers (revenue, margin, backlog, order book) unverified by audited filings or credible diligence?
*Why it kills deals (automotive reading):* Auto backlogs are often soft. Unverified means the thesis is unsupported.

**B7.** Is the target's quality or delivery standing at risk (IATF 16949 lapse, OEM probation, controlled shipping, major recall history)?
*Why it kills deals (automotive reading):* Quality status gates future OEM awards.

**B9.** Is ownership of core IP, licenses, or critical supply (chips, cells, rare earths) unclear, contingent on a change-of-control clause, or exposed to export controls?
*Why it kills deals (automotive reading):* Buyer may not get what it thinks it is buying.

**B10.** Does the deal depend on trade or subsidy conditions (tariffs, EV credits, local content rules) that could reverse and have no pass-through or fallback?
*Why it kills deals (automotive reading):* Policy risk gets priced as if it were permanent.

B1, B5, B8 and B11 read the same as the core.

## 4. Dimension prompts

Original wording for the bullets the core generalized. Answer the core bullet using this reading for automotive deals.

**D2 (customer and contract quality)**
- How much revenue is aftermarket or recurring versus program-based?

**D3 (technology and cycle timing)**
- Is the product position on the right side of the powertrain and software transition (EV, hybrid, ICE, ADAS, software-defined vehicle)?

**D9 (maintenance and lifecycle burden)**
- **Asset age and deferred work:** average age of presses, lines, tooling and tools. What overhauls, rebuilds or replacements are scheduled or overdue in the next 5 years, and what do they cost?
- **Serviceability of the product:** how costly and hard is it to repair (sealed modules, battery packs, special tools, labor hours, parts availability)? Does that cost fall on the target, the customer, or the OEM?

## 5. Pack breakers

None defined in v0.1. Record `pack_breakers` as `n/a`.

## 6. Pack change log

- v0.1: extracted from core v0.1 (the all-automotive method). No content change; wording kept verbatim as readings and prompts above.
