# Packs (specializations)

A pack is a sector's layer on top of the core method. The core stays sector-neutral. A pack carries what only that industry knows.

## What a pack may do

- Set its own scope (regions, deal size, dates, which companies count).
- Define the allowed values for the core fields `sector`, `subsector` and `acquirer_role`.
- Sharpen the wording of any core breaker or dimension question for the sector ("sector reading"), and add sector prompts under a dimension.
- Add pack breakers (id `<pack>_b1`, `<pack>_b2`, ...). They follow the same rule as core breakers.
- Add extra fields in `ext.csv` (keyed by `assessment_id`) when the core tables cannot hold them.

## What a pack may not do

- Change weights, grade bands, the order of checks, or the unknown rule.
- Delete or skip a core question. If a core question seems not to apply, answer it `N` and add an evidence row that says why the risk cannot arise (for example, "target owns no plants"). `N` needs evidence like any other answer.
- Change a core threshold on its own authority. Threshold changes go through the change log and a backtest.

## Using a pack

1. Set the deal's `sector` to the pack id. Leave it as `general` to grade with the core alone.
2. Answer each core question using the pack's reading of it.
3. Record the versions used in the assessment's `method_version`, e.g. `core-0.3;automotive-0.1`.
4. If the pack defines breakers, record the combined result in the assessment's `pack_breakers` (`clear`, `mitigated`, `unmitigated`); use `n/a` when the pack defines none.

## Adding a pack

Create `packs/<id>/pack.md` with these sections, in this order: Scope; Field values; Breaker readings (B1 to B11, only those it sharpens, original core wording kept beside the sector reading); Dimension prompts; Pack breakers (if any); Pack change log. Add a row to the table in the top-level README. Keep the core untouched unless the change is a core change and logged as one.

A pack's v0 is an extraction or a draft, not a calibrated instrument. Backtest it on 20 or more closed deals in its own sector before changing its thresholds.
