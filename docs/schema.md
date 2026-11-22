# Schema: `data/deals.csv`

One row per deal. Failed, withdrawn and blocked deals go in the same table as closed ones.

## Sector

| Field | Type | Notes |
|-------|------|-------|
| `sector` | text | Lowercase sector track name, matching a file in `sectors/`. Every row must name its track |

## Identification

| Field | Type | Notes |
|-------|------|-------|
| `deal_id` | text | `YYYY-acquirer-target` in lowercase, e.g. `2023-acquirerco-targetco` |
| `acquirer` | text | Legal or common name |
| `acquirer_type` | enum | Vocabulary set by the sector addendum (automotive: `oem`, `tier1`, `tier2`, `pe`, `tech`, `other`) |
| `acquirer_country` | text | ISO 3166 alpha-2 |
| `target` | text | |
| `target_segment` | enum | Segment vocabulary set by the sector addendum (automotive: `powertrain`, `ev_battery`, `adas_software`, `chassis`, `interior`, `electronics`, `thermal`, `aftermarket`, `other`) |
| `target_country` | text | ISO 3166 alpha-2 |
| `deal_type` | enum | `acquisition`, `merger`, `carve_out`, `minority_stake`, `jv` |

## Timing and status

| Field | Type | Notes |
|-------|------|-------|
| `announced_date` | date | `YYYY-MM-DD` |
| `closed_date` | date | Blank if not closed |
| `status` | enum | `rumored`, `announced`, `pending`, `closed`, `withdrawn`, `blocked` |
| `status_reason` | text | Why it was withdrawn, blocked, or delayed. Blank if none |

## Value

| Field | Type | Notes |
|-------|------|-------|
| `value_usd_m` | number | Enterprise value in USD millions. Blank if unknown |
| `value_basis` | enum | `disclosed`, `reported`, `estimated`, `unknown` |
| `ev_revenue` | number | Blank if unknown |
| `ev_ebitda` | number | Blank if unknown |
| `multiple_basis` | text | Which period (LTM, forward) and which source |

## Maintenance and upkeep figures

All in USD millions unless noted. Blank means unknown. Definitions are in `docs/core-methodology.md` section 3a.

| Field | Type | Notes |
|-------|------|-------|
| `maint_capex_usd_m` | number | Annual capex needed to hold current output |
| `growth_capex_usd_m` | number | Annual capex for expansion |
| `catchup_capex_usd_m` | number | Deferred or overdue work, total |
| `warranty_pct_revenue` | number | Warranty expense as % of revenue, latest year |
| `warranty_trend` | enum | `rising`, `flat`, `falling`, `unknown` (3-year) |
| `known_upcoming_costs_usd_m` | number | 5-year known costs: catch-up, scheduled overhauls, mandated retrofits, unreserved claims |
| `maint_adj_ev_ebitda` | number | EV divided by maintenance-adjusted EBITDA |
| `maint_basis` | enum | `disclosed`, `reported`, `estimated`, `unknown` |

## Gate 1: Breakers (values `Y`, `N`, `U`, `M`)

`b1_regulatory`, `b2_customer_concentration`, `b3_platform_end_of_life`, `b4_liabilities`, `b5_funding`, `b6_unverified_numbers`, `b7_quality_standing`, `b8_labor_blocks`, `b9_ip_supply`, `b10_policy_dependency`, `b11_catchup_capex`

Question wording is in `docs/core-methodology.md`; sector probes are in `sectors/<sector>.md`. `M` requires a note in `breaker_notes`.

| Field | Type | Notes |
|-------|------|-------|
| `breaker_notes` | text | Evidence and mitigations, short. Use `;` to separate items |

## Gate 2: Dimension scores (integers 0 to 4)

`d1_strategic_fit`, `d2_customer_contract`, `d3_tech_cycle`, `d4_financial_quality`, `d5_price_structure`, `d6_synergies`, `d7_integration`, `d8_regulatory_geo`, `d9_maintenance_lifecycle`

## Grade

| Field | Type | Notes |
|-------|------|-------|
| `score_pct` | number | Weighted score as a percent, 0 to 100 (see methodology) |
| `grade` | enum | `great`, `good`, `okay`, `bad`, `horrid` |
| `grade_basis` | enum | `prospective` or `retrospective` |
| `grade_perspective` | enum | `acquirer`, `target_holders`, `neutral` |
| `grade_date` | date | When this grade was assigned |
| `outcome_grade` | enum | Hindsight grade, filled 3+ years after close. Blank until then |
| `outcome_notes` | text | What actually happened |

## Provenance

| Field | Type | Notes |
|-------|------|-------|
| `source_url` | text | Primary source for the deal facts. Separate several with a space |
| `source_type` | enum | `filing`, `press_release`, `regulator`, `news`, `other` |
| `confidence` | enum | `high`, `medium`, `low` |
| `last_verified` | date | `YYYY-MM-DD` |
| `notes` | text | Anything else |

## Conventions

- Blank means unknown or not applicable. Do not use `0`, `N/A` or `-` as placeholders.
- Currency is USD. Say in `multiple_basis` or `notes` if converted, and at what rate and date.
- Dates are ISO `YYYY-MM-DD`.
- Text with commas must be quoted. Mobile tip: use `;` instead of commas inside text fields.
