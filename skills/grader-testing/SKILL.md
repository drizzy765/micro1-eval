# Skill: grader testing

## When to use

Any change to `grader/`, to gold fields, to `parse_amount_ngn`, or to how the runner loads answers.

## Invariants

- No network in the grader.
- False CONFIRMED (predicted CONFIRMED, gold not CONFIRMED) always scores 0.0 and sets `catastrophic_false_confirmed`.
- `passed` requires exact verdict match AND every compared field match AND no schema errors.
- Score otherwise is `0.6 * verdict + 0.4 * field_fraction`.
- `reasons` are not compared.
- `2k5`, `2.5k` and `2500` are the same amount.

## Commands (PowerShell)

```powershell
python -m pytest -q
python -m pytest tests/test_grader.py tests/test_reference_decoy.py -q
```

## When you add a field to gold

1. Add it to `COMPARE_FIELDS` only if a model should be required to produce it.
2. Update every task's `gold`, `reference_answer` and `decoy_answer`.
3. Extend tests rather than deleting the old ones.

## When a model output will not parse

The runner may coerce a broken payload to `UNVERIFIED` with `parse_error: true`. That prediction must not pass a CONFIRMED or SUSPICIOUS gold. Do not "helpfully" map free text like "looks legit" to CONFIRMED.

## Do not

- Soften the catastrophic rule to raise a leaderboard score
- Compare raw strings for amounts ("₦2,500" vs 2500 must agree)
- Hide a failing decoy by editing it until it accidentally passes
