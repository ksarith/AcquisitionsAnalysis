# Assessment report template

Keep the report short enough to read on a phone. Lead with the result. Everything in it comes from the assessment rows and the tool output; nothing new is introduced in the report. Include only the sections for the sides that were in scope.

```
# {acquirer} / {target}: OVERALL {overall_integrity_verdict}{ (provisional)}

Assessment {assessment_id}
Scope {structural|negotiation|both}; basis {prospective|retrospective}, cutoff {information_cutoff}; perspective {perspective}
Pack {pack or "core only"}; method {method_version}; assessed {assessment_date} by {assessor}
Computed by tools/calculate_grade.py {version}; validated by tools/validate_data.py ({n} errors, {n} warnings)

## Why this verdict
One or two sentences: which side drove it (overall_driver), which ceiling or predicate decided it, and the single biggest driver.

## Structural: {structural_grade} ({score_pct}%)
### Breakers (B1 to B11, plus pack breakers)
| ID | Answer | Evidence | Note |
Only list the breakers that are not a clean N, then one line: "All other breakers N, with evidence ids ...".
### Dimensions
| Dim | Score | One-line reason | Evidence ids |
### Maintenance figures
Plain EV/EBITDA {x}; maintenance-adjusted {y} (proxy defined by this method, not an accounting measure); price adjusted for known costs {z}.
State anything blank and why, the EBITDA period, and whether figures are disclosed, reported or estimated.

## Negotiation: {negotiation_classification} (NQS {nqs})
Active failure predicates: {F1/F2/F3 or none}. Multiplicative diagnostic (experimental, not in the verdict): {nq_multiplicative}.
| Dim | Score | One-line reason | Evidence ids | Direct or inferred |
Unknown (blank) dimensions are listed here and explain why the negotiation is Unresolved.
State how much of the negotiation record was observable, and the cutoff used.

## Unknowns and evidence gaps
Each unresolved `U` breaker, each blank negotiation dimension, each dimension with thin evidence, and the source that would resolve it.

## Contradictions
Evidence that points both ways, and how the answer treated it.

## What would change the verdict
The two or three facts that, if established, would move the verdict, and in which direction.

## Limits
Same-lineage assessment unless an independent check was run. Any step done by hand. Disclaimer: see Disclaimer.md.
```

Rules for the report:
- Evidence ids refer to rows in `data/evidence.csv`. Never cite a source that is not in the ledger.
- Do not repeat quotations. Summarize in your own words.
- If any assessment step was done by hand or any tool was not run, say so under Limits and do not call the verdict verified.
- Do not recommend buying, selling or pricing. The verdict is an opinion on deal quality and negotiation conduct.
