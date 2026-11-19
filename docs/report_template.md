# Assessment report template

Keep the report short enough to read on a phone. Lead with the result. Everything in it comes from the assessment rows and the tool output; nothing new is introduced in the report.

```
# {acquirer} / {target}: {grade} ({score_pct}%)

Assessment {assessment_id}
Basis {prospective|retrospective}, cutoff {information_cutoff}; perspective {perspective}
Pack {pack or "core only"}; method {method_version}; assessed {assessment_date} by {assessor}
Grade computed by tools/calculate_grade.py {version}; validated by tools/validate_data.py ({n} errors, {n} warnings)

## Why this grade
One or two sentences: which ceiling decided it (breakers, a zero dimension, or the score band), and the single biggest driver.

## Breakers (B1 to B11, plus pack breakers)
| ID | Answer | Evidence | Note |
Only list the breakers that are not a clean N, then one line: "All other breakers N, with evidence ids ...".

## Dimensions
| Dim | Score | One-line reason | Evidence ids |

## Maintenance figures
Plain EV/EBITDA {x}; maintenance-adjusted {y} (proxy defined by this method, not an accounting measure); price adjusted for known costs {z}.
State anything blank and why. State the EBITDA period and whether figures are disclosed, reported or estimated.

## Unknowns and evidence gaps
Each unresolved `U`, each dimension with thin evidence, and the source that would resolve it.

## Contradictions
Evidence that points both ways, and how the answer treated it.

## What would change the grade
The two or three facts that, if established, would move the grade, and in which direction.

## Limits
Same-lineage assessment unless an independent check was run. Any step done by hand. Disclaimer: Use at own risk.
```

Rules for the report:
- Evidence ids refer to rows in `data/evidence.csv`. Never cite a source that is not in the ledger.
- Do not repeat quotations. Summarize in your own words.
- If any assessment step was done by hand or any tool was not run, say so under Limits and do not call the grade verified.
- Do not recommend buying, selling or pricing. The grade is an opinion on deal quality.
