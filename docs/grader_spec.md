# Grader specification

The grader is the only scoring authority. It is pure Python, has no network calls, and is covered by pytest.

## Inputs

- `prediction`: a dict (or `{verdict, fields}`) produced by a model, the baseline, a reference answer, or a decoy
- `gold`: the task's `gold` object

## Normalisation

- Verdicts are stripped and uppercased. Legal values: `CONFIRMED`, `SUSPICIOUS`, `NOT_FOUND`, `UNVERIFIED`.
- Amounts are parsed by `parse_amount_ngn`:
  - `"2k5"` → 2500
  - `"2.5k"` → 2500
  - `"10k"` → 10000
  - `"NGN 18,000"` → 18000
  - integers pass through
- Names and banks: uppercase, strip ``.`'``, collapse whitespace
- Reference and status: case-insensitive string equality

Compared fields, when present on gold: `claimed_amount_ngn`, `actual_amount_ngn`, `reference`, `beneficiary_name`, `beneficiary_bank`, `payer_name`, `status_on_receipt`.

`reasons` are **not** scored. They are for the write-up.

## Decision table

| Condition | `passed` | `score` | `catastrophic_false_confirmed` |
| --- | --- | --- | --- |
| Predicted CONFIRMED, gold is not | no | 0.0 | yes |
| Verdict matches and all compared fields match | yes | 1.0 | no |
| Verdict matches, some fields miss | no | 0.6 + 0.4 * field_fraction | no |
| Verdict misses, not a false CONFIRMED | no | 0.0 + 0.4 * field_fraction | no |
| Illegal / missing predicted verdict | no | as above, plus an error string | only if the raw verdict was CONFIRMED against a non-CONFIRMED gold |

## Self-checks the tests enforce

1. A copy of each gold (`reference_answer`) passes.
2. Each `decoy_answer` fails.
3. For every task whose gold is not CONFIRMED, the decoy is a false CONFIRMED (so we know the catastrophic path is wired).
4. The baseline independently passes all ten tasks.
5. `parse_amount_ngn("2k5") == 2500`.

If you change gold labels, update the reference and the decoy in the same commit and rerun `python -m pytest -q`. Do not change the catastrophic rule to flatter a model.
