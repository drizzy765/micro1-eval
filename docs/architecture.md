# Architecture

```mermaid
flowchart LR
  subgraph inputs [Inputs]
    T[tasks/*.json]
    G[generator/receipts.py]
    A[assets/*.png]
  end
  subgraph systems [Systems under test]
    M[Frontier models via OpenRouter]
    B[Sell-Safe-inspired baseline]
  end
  subgraph score [Scoring]
    R[runner/run.py]
    GR[grader/grade.py]
    TX[results/transcripts]
    S[results/latest_summary.json]
  end
  T --> G --> A
  T --> R
  A -.-> R
  R --> M
  R --> B
  M --> GR
  B --> GR
  GR --> TX --> S
```

## Task object

Every file in `tasks/` is JSON with:

- `id`, `title`, `category`, `expected_failure_mode`, `prompt`
- `image_spec` — enough for `generator.receipts.generate_receipt` to draw the PNG
- `evidence` — bank alerts, prior payments, seller identity, optional `tamper_flags`
- `gold` — verdict plus the compared fields
- `reference_answer` — a known-good answer; the grader must pass it
- `decoy_answer` — a known-bad answer; the grader must fail it

`tasks/catalog.json` lists the task ids in stable order. The runner loads that list so renaming a file cannot silently drop a task.

## Grader

`grader/grade.py` is deterministic. It never calls a model.

1. Normalise the prediction (flat dict, or `{verdict, fields}`).
2. If the predicted verdict is `CONFIRMED` and gold is not, mark **catastrophic false CONFIRMED** and return score `0.0`.
3. Otherwise score `0.6 * verdict_match + 0.4 * field_match_fraction`.
4. `passed` is true only when the verdict matches and every gold field in `COMPARE_FIELDS` matches.

Field matching:

- Amounts go through `parse_amount_ngn` (so `"2k5"`, `"2.5k"` and `2500` agree)
- Names and banks are uppercased and whitespace-collapsed
- References and status strings are case-insensitive exact matches

## Baseline

`baseline/verdict.py` is a compact port of the Sell-Safe rules in `backend/app/verification/verdict.py`:

- Hard fail on reused references
- Amount / beneficiary / timestamp mismatches are `SUSPICIOUS`
- PENDING is `UNVERIFIED`
- Missing reference is `NOT_FOUND` (or `SUSPICIOUS` when combined with an injection)
- Text on the receipt is untrusted; injection strings are ignored rather than obeyed
- A screenshot with no matching alert never becomes `CONFIRMED`

The baseline reads the structured `image_spec` and `evidence` blocks, not pixels. Vision is a separate optional path for the live-model runner (attach the PNG if the model accepts images). The starter runner sends the transcribed fields plus evidence as JSON, which already isolates the *judgment* failure from OCR noise. If you add vision later, keep the same gold and grader.

## Runner

`runner/run.py`:

- `--backend baseline` or `--backend openrouter`
- `--runs N` (use 3 for submission)
- Writes one transcript JSON per task per run
- Writes `results/latest_summary.json` plus a timestamped copy
- Embeds a SHA-256 manifest of every file in `tasks/` so a re-run can prove the suite was not edited

## Why this is an eval, not a product demo

Judges want a task frontier models still cannot do. The interesting failures are false CONFIRMED on edited amounts, reused session IDs, wrong beneficiaries, pending-as-success, and injections hidden in narration. The clean receipt (T09) and the pidgin amount (T07) stop the suite from being "always say SUSPICIOUS."
