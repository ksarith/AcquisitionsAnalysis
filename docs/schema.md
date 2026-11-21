# Schema

Three tables in `data/`, joined by id. A deal is one row; each time a deal is assessed is one **assessment**; every answer an assessment gives is backed by **evidence** rows. One deal can carry several independent assessments (prospective and retrospective, acquirer and neutral, structural and negotiation) without overwriting each other, and every answer can be audited back to a source.

```
deals.csv (deal_id)  <-  assessments.csv (assessment_id, deal_id)  <-  evidence.csv (evidence_id, assessment_id, question_id)
```

An assessment covers one or both **sides**: the deal itself (**structural**: breakers B1 to B11, dimensions D1 to D9) and how it was negotiated (**negotiation**: N1 to N10). The `assessment_scope` field says which. Both sides sit in the same row; the fields of a side that is out of scope stay blank.

A sector's pack ([`../packs/README.md`](../packs/README.md)) defines the allowed values for `sector`, `subsector` and `acquirer_role`, and may add fields in its own `ext.csv` keyed by `assessment_id`.

The check tools read this file's field lists as the source of truth for column names and order: [`../tools/validate_data.py`](../tools/validate_data.py). Calculation rules: [`methodology.md`](methodology.md).

## deals.csv

One row per deal. Failed, withdrawn and blocked deals go in the same table as closed ones. Deal facts only: no grades, no judgments about the deal.

| Field | Type | Notes |
|-------|------|-------|
| `deal_id` | text | `YYYY-acquirer-target` in lowercase, e.g. `2023-acquirerco-targetco` |
| `acquirer` | text | Legal or common name |
| `acquirer_type` | enum | `strategic`, `pe`, `other` |
| `acquirer_role` | text | Sector detail from the pack (e.g. automotive: `oem`, `tier1`). Blank if no pack or not applicable |
| `acquirer_country` | text | ISO 3166 alpha-2 |
| `target` | text |  |
| `sector` | text | The pack id (e.g. `automotive`), or `general` to grade with the core alone |
| `subsector` | text | Allowed values come from the pack. Blank for `general` |
| `target_country` | text | ISO 3166 alpha-2 |
| `deal_type` | enum | `acquisition`, `merger`, `carve_out`, `minority_stake`, `jv` |
| `announced_date` | date | `YYYY-MM-DD` |
| `closed_date` | date | Blank if not closed |
| `status` | enum | `rumored`, `announced`, `pending`, `closed`, `withdrawn`, `blocked` |
| `status_reason` | text | Why it was withdrawn, blocked, or delayed. Blank if none |
| `value_usd_m` | number | Enterprise value in USD millions. Blank if unknown |
| `value_basis` | enum | `disclosed`, `reported`, `estimated`, `unknown` |
| `ev_revenue` | number | Blank if unknown |
| `ev_ebitda` | number | Plain (unadjusted) multiple. Blank if unknown |
| `multiple_basis` | text | Which period (LTM, forward) and which source |
| `outcome_notes` | text | What actually happened, for backtesting. Blank until known |
| `source_url` | text | Primary source for the deal facts. Separate several with a space |
| `source_type` | enum | `filing`, `press_release`, `regulator`, `news`, `other` |
| `confidence` | enum | `high`, `medium`, `low` |
| `last_verified` | date | `YYYY-MM-DD` |
| `notes` | text | Anything else |

## assessments.csv

One row per assessment of a deal. Computed fields are calculated by `tools/calculate_grade.py` and checked against the recorded values by `tools/validate_data.py`; do not hand-edit them.

| Field | Type | Notes |
|-------|------|-------|
| `assessment_id` | text | Unique. Suggested form: `<deal_id>_<basis>_<perspective>_<n>` |
| `deal_id` | text | Must exist in `deals.csv` |
| `grade_basis` | enum | `prospective` or `retrospective`. Never mix in one assessment |
| `grade_perspective` | enum | `acquirer`, `target_holders`, `neutral` |
| `assessment_scope` | enum | `structural` (breakers and dimensions), `negotiation` (N1 to N10), or `both`. Fields of a side that is out of scope stay blank |
| `assessment_date` | date | When this assessment was made |
| `information_cutoff` | date | Latest date any cited evidence may carry. Required for `prospective` (normally the announcement date); blank for `retrospective` |
| `assessor` | text | Who or what made the assessment, as claimed: human, model or agent, with version if known. A claim, not provenance |
| `method_version` | text | Layer versions, separated by `;`, e.g. `core-0.3;negotiation-0.1;automotive-0.1`. Use `core-0.3` for structural only, `negotiation-0.1` for negotiation only |
| `b1_regulatory` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B1. Blank if scope is `negotiation` |
| `b2_customer_concentration` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B2. Blank if scope is `negotiation` |
| `b3_platform_end_of_life` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B3. Blank if scope is `negotiation` |
| `b4_liabilities` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B4. Blank if scope is `negotiation` |
| `b5_funding` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B5. Blank if scope is `negotiation` |
| `b6_unverified_numbers` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B6. Blank if scope is `negotiation` |
| `b7_quality_standing` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B7. Blank if scope is `negotiation` |
| `b8_labor_blocks` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B8. Blank if scope is `negotiation` |
| `b9_ip_supply` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B9. Blank if scope is `negotiation` |
| `b10_policy_dependency` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B10. Blank if scope is `negotiation` |
| `b11_catchup_capex` | enum | `Y`, `N`, `U`, `M` (see methodology section 2). Question B11. Blank if scope is `negotiation` |
| `pack_breakers` | enum | Combined result of the pack's own breakers: `n/a` (none defined), `clear`, `mitigated`, `unmitigated`. Blank if scope is `negotiation` |
| `breaker_notes` | text | Evidence summary and mitigations, short. Required when any answer is `M`. Use `;` to separate items |
| `d1_strategic_fit` | int | 0 to 4. Dimension D1: Strategic fit and rationale (weight 2). Blank if scope is `negotiation` |
| `d2_customer_contract` | int | 0 to 4. Dimension D2: Customer and contract quality (weight 2). Blank if scope is `negotiation` |
| `d3_tech_cycle` | int | 0 to 4. Dimension D3: Technology and cycle timing (weight 2). Blank if scope is `negotiation` |
| `d4_financial_quality` | int | 0 to 4. Dimension D4: Financial quality (weight 2). Blank if scope is `negotiation` |
| `d5_price_structure` | int | 0 to 4. Dimension D5: Price and structure (weight 2). Blank if scope is `negotiation` |
| `d6_synergies` | int | 0 to 4. Dimension D6: Synergy credibility (weight 1). Blank if scope is `negotiation` |
| `d7_integration` | int | 0 to 4. Dimension D7: Integration and people (weight 1). Blank if scope is `negotiation` |
| `d8_regulatory_geo` | int | 0 to 4. Dimension D8: Regulatory and geopolitical exposure (weight 1). Blank if scope is `negotiation` |
| `d9_maintenance_lifecycle` | int | 0 to 4. Dimension D9: Maintenance and lifecycle burden (weight 2). Blank if scope is `negotiation` |
| `n1_preparation` | int | 0 to 100, whole numbers. Negotiation dimension N1: Preparation (weight 10%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `n2_information_discovery` | int | 0 to 100, whole numbers. Negotiation dimension N2: Information discovery (weight 15%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `n3_value_creation` | int | 0 to 100, whole numbers. Negotiation dimension N3: Value creation (weight 15%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `n4_communication` | int | 0 to 100, whole numbers. Negotiation dimension N4: Communication discipline (weight 10%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `n5_value_capture` | int | 0 to 100, whole numbers. Negotiation dimension N5: Value capture (weight 10%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `n6_objective_alignment` | int | 0 to 100, whole numbers. Negotiation dimension N6: Objective alignment (weight 10%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `n7_relationship` | int | 0 to 100, whole numbers. Negotiation dimension N7: Relationship preservation (weight 10%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `n8_risk_allocation` | int | 0 to 100, whole numbers. Negotiation dimension N8: Risk allocation (weight 8%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `n9_epistemic_integrity` | int | 0 to 100, whole numbers. Negotiation dimension N9: Epistemic integrity (weight 8%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `n10_procedural_legitimacy` | int | 0 to 100, whole numbers. Negotiation dimension N10: Procedural legitimacy (weight 4%). Blank = unknown (unresolved). Blank if scope is `structural` |
| `negotiation_notes` | text | Evidence summary for the negotiation answers, short. Use `;` to separate items |
| `ebitda_usd_m` | number | Target EBITDA, plain, USD millions. State the period in `maint_notes`. Blank if unknown |
| `maint_capex_usd_m` | number | Annual capex needed to hold current output. Blank if unknown |
| `growth_capex_usd_m` | number | Annual capex for expansion |
| `catchup_capex_usd_m` | number | Deferred or overdue work, total (one-time) |
| `warranty_pct_revenue` | number | Warranty expense as % of revenue, latest year |
| `warranty_trend` | enum | `rising`, `flat`, `falling`, `unknown` (3-year) |
| `warranty_normalization_usd_m` | number | Normalized annual warranty cost minus what is already expensed, if positive; `0` if not positive. Blank if unknown |
| `known_upcoming_costs_usd_m` | number | 5-year known costs, undiscounted: catch-up, scheduled overhauls, mandated retrofits, unreserved claims. Includes `catchup_capex_usd_m` |
| `maint_basis` | enum | `disclosed`, `reported`, `estimated`, `unknown` |
| `maint_notes` | text | How the figures were derived; the EBITDA period; any discounting. Required if adjusted EBITDA is not positive |
| `maint_adj_ebitda_usd_m` | number | Computed: ebitda - maint_capex - warranty_normalization. Blank if any input is blank |
| `maint_adj_ev_ebitda` | number | Computed: deal `value_usd_m` / adjusted EBITDA. Blank if adjusted EBITDA is not positive or an input is blank |
| `price_adj_for_known_usd_m` | number | Computed: deal `value_usd_m` - known_upcoming_costs. Blank if an input is blank |
| `weighted_score` | int | Computed: sum of dimension score x weight, 0 to 60. Blank if scope is `negotiation` |
| `score_pct` | number | Computed: weighted_score / 60 x 100, one decimal. Blank if scope is `negotiation` |
| `structural_grade` | enum | Computed: `great`, `good`, `okay`, `bad`, `horrid` (methodology section 5). Blank if scope is `negotiation` |
| `nqs` | number | Computed: Negotiation Quality Score, 0 to 100, one decimal. Blank if any N dimension is unknown or the scope is `structural` |
| `negotiation_classification` | enum | Computed: `exceptional`, `high_quality`, `competent`, `marginal`, `poor`, `failed`, `unresolved`. Blank if scope is `structural` |
| `failure_predicates` | text | Computed: fired predicate codes separated by `;` (`F1`, `F2`, `F3`). Blank if none |
| `nq_multiplicative` | number | Computed, experimental diagnostic only (not used in any verdict): product of four factors, 0 to 1, three decimals. Blank unless all inputs are present |
| `overall_integrity_verdict` | enum | Computed: `great`, `good`, `okay`, `bad`, `horrid`: the worse of the in-scope sides, on one shared scale |
| `overall_driver` | enum | Computed: `structural`, `negotiation`, `both`: which in-scope side set the verdict |
| `overall_provisional` | enum | Computed: `yes` if any breaker is `U` or the negotiation is `unresolved`, else `no` |
| `notes` | text | Anything else |

## evidence.csv

One row per piece of evidence bearing on one question of one assessment. A source that bears on several questions gets one row per question.

| Field | Type | Notes |
|-------|------|-------|
| `evidence_id` | text | Unique |
| `assessment_id` | text | Must exist in `assessments.csv` |
| `question_id` | text | `b1` to `b11`, `d1` to `d9`, `n1` to `n10`, `maint` (maintenance figures), or a pack breaker id such as `automotive_b1` |
| `source_url` | text | The original source |
| `source_date` | date | Publication date of the source. Required for `prospective` assessments |
| `accessed_date` | date | When it was retrieved |
| `evidence_type` | enum | `filing`, `press_release`, `regulator`, `analyst_estimate`, `news`, `interview`, `internal`, `negative_finding`, `inference`, `other`. `negative_finding`: what was searched and not found. `inference`: a conclusion drawn from other evidence, not directly observed |
| `extracted_claim` | text | What the source establishes, in your own words, short. Not a copy of paid-database text |
| `bearing` | enum | Relation to the answer recorded for `question_id`: `supports`, `contradicts`, `inconclusive` |
| `confidence` | enum | `high`, `medium`, `low`: reliability of this evidence |

## Conventions

- Blank means unknown or not applicable. Do not use `0`, `N/A` or `-` as placeholders. (Exceptions: `pack_breakers` uses `n/a` when the pack defines no breakers; `warranty_normalization_usd_m` uses `0` when the normalization is not positive.)
- A blank negotiation dimension means **unknown**, and an unknown is never a pass (methodology section 4).
- Currency is USD. Say in `multiple_basis`, `maint_notes` or `notes` if converted, and at what rate and date.
- Dates are ISO `YYYY-MM-DD`.
- Text with commas must be quoted. Mobile tip: use `;` instead of commas inside text fields.
- Do not commit paid-database exports. `extracted_claim` is your own summary.

## Evidence rules the checker enforces

- Every breaker answer other than `U`, and every negotiation score that is not blank, needs at least one `supports` evidence row for that question. `N` is not an assumption: an answer of "nothing found" needs a row (type `negative_finding`) saying what was searched and where. A question that seems not to apply is answered `N` with a row that says why.
- `U` and a blank negotiation dimension need no evidence and are risks until resolved.
- Any `M` needs `breaker_notes`.
- A `prospective` assessment needs `information_cutoff`, and every evidence row it cites needs a `source_date` on or before that cutoff.
- Out-of-scope sides must be blank: an assessment with scope `negotiation` carries no breaker answers, dimension scores, grade or maintenance figures, and one with scope `structural` carries no negotiation scores.
- Dimensions without evidence rows are reported as warnings, not errors (starting value; see methodology). A negotiation score whose only supporting evidence is of type `inference` is reported as a warning, and so is `internal` evidence in a prospective assessment (confirm it was available to the assessor's perspective at the time).
