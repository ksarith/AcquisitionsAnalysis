# Schema

Assessment data lives in three tables under `data/`: `deals.csv` (facts about a deal), `assessments.csv` (one assessment run: answers and computed results) and `evidence.csv` (the evidence ledger that every answer cites). `tools/validate_data.py` reads this file and checks the tables against it: the fields listed in each section, in order, are the table header. Blank means unknown or not applicable: never `0`, `N/A` or `-` as placeholders. Dates are ISO `YYYY-MM-DD`. Amounts are USD millions unless noted. Text with commas must be quoted; mobile tip: use `;` instead of commas inside text fields. Computed fields are never hand-edited; `tools/calculate_grade.py` fills them and the validator checks them.

One row per deal in `deals.csv`: stable facts only. Answers, scores and grades belong to assessments; a deal carries any number of assessments and they never overwrite each other.

## deals.csv

| `deal_id` | text | `YYYY-acquirer-target` in lowercase, e.g. `2020-examplebuyer-exampletarget`. Unique |
| `acquirer` | text | Legal or common name |
| `acquirer_type` | enum | `strategic`, `pe`, `other` |
| `acquirer_role` | text | Sector vocabulary set by the pack (automotive: `oem`, `tier1`, `tier2`, `pe`, `tech`, `other`). Blank when no pack applies |
| `acquirer_country` | text | ISO 3166 alpha-2 |
| `target` | text |  |
| `sector` | text | Pack id, or `general` when grade with the core alone |
| `subsector` | text | Sector vocabulary set by the pack (automotive: `powertrain`, `ev_battery`, `adas_software`, `chassis`, `interior`, `electronics`, `thermal`, `aftermarket`, `other`) |
| `target_country` | text | ISO 3166 alpha-2 |
| `deal_type` | enum | `acquisition`, `merger`, `carve_out`, `minority_stake`, `jv` |
| `announced_date` | date | Also the default `information_cutoff` for prospective assessments |
| `closed_date` | date | Blank if not closed |
| `status` | enum | `rumored`, `announced`, `pending`, `closed`, `withdrawn`, `blocked` |
| `status_reason` | text | Why it was withdrawn, blocked, or delayed. Blank if none |
| `value_usd_m` | number | Enterprise value. Feeds the maintenance-adjusted multiples |
| `value_basis` | enum | `disclosed`, `reported`, `estimated`, `unknown` |
| `ev_revenue` | number | Blank if unknown |
| `ev_ebitda` | number | Plain multiple, not maintenance-adjusted. Blank if unknown |
| `multiple_basis` | text | Which period (LTM, forward) and which source |
| `outcome_notes` | text | What actually happened, filled 3+ years after close; feeds retrospective calibration |
| `source_url` | text | Primary source for the deal facts. Separate several with a space |
| `source_type` | enum | `filing`, `press_release`, `regulator`, `news`, `other` |
| `confidence` | enum | `high`, `medium`, `low` |
| `last_verified` | date |  |
| `notes` | text | Anything else |

## assessments.csv

| `assessment_id` | text | Lowercase; unique. Recommended form `{deal_id}_{basis}_{perspective}_{n}` |
| `deal_id` | text | Must exist in `deals.csv` |
| `grade_basis` | enum | `prospective` (needs `information_cutoff`) or `retrospective` |
| `grade_perspective` | enum | `acquirer`, `target_holders`, `neutral` |
| `assessment_scope` | enum | `structural`, `negotiation`, `both`. Fields of a side out of scope stay blank; the validator checks this |
| `assessment_date` | date | When the assessment was made |
| `information_cutoff` | date | Evidence dated after it cannot be used; the validator enforces this. Required for prospective |
| `assessor` | text | Who or what gathered the answers |
| `method_version` | text | Layers used, e.g. `core-0.3;negotiation-0.1;automotive-0.1` |
| `b1_regulatory` | enum | Credible path to clearance? Values `Y`, `N`, `U`, `M` (mitigated). Every `Y`/`N`/`M` needs a supporting evidence row; any `M` also needs `breaker_notes` |
| `b2_customer_concentration` | enum | One customer near 40%? Same values and evidence rules as the other breakers |
| `b3_platform_end_of_life` | enum | End-of-life revenue base? Same values and evidence rules |
| `b4_liabilities` | enum | Unquantified or uncapped liabilities? Same values and evidence rules |
| `b5_funding` | enum | Funding stress? Same values and evidence rules |
| `b6_unverified_numbers` | enum | Numbers unverified? Same values and evidence rules |
| `b7_quality_standing` | enum | Quality standing at risk? Same values and evidence rules |
| `b8_labor_blocks` | enum | Labor or government blocks? Same values and evidence rules |
| `b9_ip_supply` | enum | IP, licenses, critical supply unclear? Same values and evidence rules |
| `b10_policy_dependency` | enum | Trade or subsidy dependency? Same values and evidence rules |
| `b11_catchup_capex` | enum | Catch-up spending above ~1x EBITDA? Same values and evidence rules |
| `pack_breakers` | enum | `n/a` when the pack defines none, else `clear`, `mitigated`, `unmitigated` |
| `breaker_notes` | text | Evidence and mitigations, short. Use `;` to separate items; required for any `M`. Contradicting evidence must be explained here, in `negotiation_notes`, or in `notes` |
| `d1_strategic_fit` | integer | Strategic fit and rationale (weight 2). 0 to 4, at least one evidence row expected |
| `d2_customer_contract` | integer | Customer and contract quality (weight 2). 0 to 4 |
| `d3_tech_cycle` | integer | Technology and cycle timing (weight 2). 0 to 4 |
| `d4_financial_quality` | integer | Financial quality (weight 2). 0 to 4; may not exceed 1 when adjusted EBITDA is not positive |
| `d5_price_structure` | integer | Price and structure (weight 2). 0 to 4 |
| `d6_synergies` | integer | Synergy credibility (weight 1). 0 to 4 |
| `d7_integration` | integer | Integration and people (weight 1). 0 to 4 |
| `d8_regulatory_geo` | integer | Regulatory and geopolitical exposure (weight 1). 0 to 4 |
| `d9_maintenance_lifecycle` | integer | Maintenance and lifecycle burden (weight 2). 0 to 4; may not exceed 2 while maintenance capex is unknown |
| `n1_preparation` | integer | Preparation (weight 10). Whole numbers 0 to 100, or blank when the record does not let you judge it; blank means unknown and is never a pass. A scored dimension needs a supporting evidence row, and a score resting only on inference-type evidence is flagged |
| `n2_information_discovery` | integer | Information discovery (weight 15). Same scoring rules as the other negotiation dimensions |
| `n3_value_creation` | integer | Value creation (weight 15). Same scoring rules |
| `n4_communication` | integer | Communication discipline (weight 10). Same scoring rules |
| `n5_value_capture` | integer | Value capture (weight 10). Same scoring rules |
| `n6_objective_alignment` | integer | Objective alignment (weight 10). Same scoring rules |
| `n7_relationship` | integer | Relationship preservation (weight 10). Same scoring rules |
| `n8_risk_allocation` | integer | Risk allocation (weight 8). Same scoring rules; below 40 fires predicate F2 |
| `n9_epistemic_integrity` | integer | Epistemic integrity (weight 8). Same scoring rules; below 40 fires predicate F1 |
| `n10_procedural_legitimacy` | integer | Procedural legitimacy (weight 4). Same scoring rules; below 40 fires predicate F3 |
| `negotiation_notes` | text | The cutoff note for a prospective negotiation assessment; observability of the record; what the blank dimensions would need |
| `ebitda_usd_m` | number | Reference EBITDA for the maintenance figures |
| `maint_capex_usd_m` | number | Annual capex needed to hold current output. Annual and recurring |
| `growth_capex_usd_m` | number | Annual capex for expansion |
| `catchup_capex_usd_m` | number | Deferred or overdue work, total. One-time |
| `warranty_pct_revenue` | number | Warranty expense as % of revenue, latest year |
| `warranty_trend` | enum | `rising`, `flat`, `falling`, `unknown` (3-year) |
| `warranty_normalization_usd_m` | number | Normalized annual warranty cost minus what is already expensed, if positive. Annual and recurring |
| `known_upcoming_costs_usd_m` | number | Undiscounted nominal 5-year known costs; includes `catchup_capex`, so it can never be smaller (the validator checks this) |
| `maint_basis` | enum | `disclosed`, `reported`, `estimated`, `unknown` |
| `maint_notes` | text | Derivation, EBITDA period, discounting, and the explanation required when adjusted EBITDA is not positive |
| `maint_adj_ebitda_usd_m` | number | Computed. Analytical proxy defined in methodology section 3a, not an accounting measure |
| `maint_adj_ev_ebitda` | number | Computed. Blank when any input is blank or adjusted EBITDA is not positive |
| `price_adj_for_known_usd_m` | number | Computed. Enterprise value minus `known_upcoming_costs_usd_m` |
| `weighted_score` | number | Computed, of 60 |
| `score_pct` | number | Computed, 0 to 100 |
| `structural_grade` | enum | Computed: `horrid`, `bad`, `okay`, `good`, `great`. Blank when the structural side is out of scope |
| `nqs` | number | Computed, 0 to 100. Blank when any negotiation dimension is unknown |
| `negotiation_classification` | enum | Computed: `exceptional`, `high_quality`, `competent`, `marginal`, `poor`, `failed`, `unresolved` |
| `failure_predicates` | text | Computed. Fired predicate codes (`F1`, `F2`, `F3`), `;`-joined. Blank when none fired |
| `nq_multiplicative` | number | Computed. Experimental diagnostic only, never in a verdict |
| `overall_integrity_verdict` | enum | Computed: worse of the in-scope sides on the shared scale `great` to `horrid` |
| `overall_driver` | enum | Computed: `structural`, `negotiation`, `both` |
| `overall_provisional` | enum | Computed: `yes` when any breaker is `U` or the negotiation is `unresolved`, else `no` |
| `notes` | text | Anything else, including a statement when a result was computed by hand and is not tool-verified |

## evidence.csv

| `evidence_id` | text | Unique, e.g. `ev-0001` |
| `assessment_id` | text | Must exist in `assessments.csv` |
| `question_id` | text | `b1` to `b11`, `d1` to `d9`, `n1` to `n10`, `maint`, or a pack breaker id like `automotive_b1` |
| `source_url` | text | Where the source lives |
| `source_date` | date | Publication date of the source; required for prospective evidence |
| `accessed_date` | date | When it was retrieved |
| `evidence_type` | enum | `filing`, `press_release`, `regulator`, `analyst_estimate`, `news`, `interview`, `internal`, `negative_finding`, `inference`, `other` |
| `extracted_claim` | text | What the source establishes, in your own words. No long quotations |
| `bearing` | enum | `supports`, `contradicts`, `inconclusive` |
| `confidence` | enum | `high`, `medium`, `low` |

## Conventions

- Every non-`U` breaker answer and every scored negotiation dimension cites at least one `supports` row in `evidence.csv`. "Nothing found" is a result: record it as a `negative_finding` row saying what was searched and where.
- Provenance of a grade: `grade_basis`, `grade_perspective`, `assessment_date`, `assessor` and `method_version` on every assessment row, so any verdict can be reproduced.
- Currency is USD. Say in `multiple_basis` or `maint_notes` if figures were converted, and at what rate and date.

## Migration notes

- The pre-v0.3 wide deals table carried answers, scores and grades; those moved into `assessments.csv`. The old `grade` column is now `structural_grade`; `grade_date` and `outcome_grade` are replaced by assessment rows (`assessment_date`, `grade_basis`) and by `outcome_notes` on the deal. Deals keep stable facts only.
- `target_segment` became `subsector`. `acquirer_type` became `strategic`/`pe`/`other`, with the old detail in `acquirer_role`; the mapping is recorded in the automotive pack.
- Rows graded before core-0.3 that are ever re-graded get new assessment rows under their own `method_version`. A recorded verdict is never rewritten.
