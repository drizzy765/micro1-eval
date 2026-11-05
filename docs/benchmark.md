# Benchmark and pass bars

## Headline metrics

| Metric | What it measures | Pass bar for a *model* | Pass bar for *our harness* |
| --- | --- | --- | --- |
| Exact-verdict accuracy | Share of predictions whose verdict matches gold | Report honestly; frontier interest starts when this is clearly below the baseline | Baseline must be 10/10 |
| Field match | Share of compared fields that match after normalisation | Secondary | Baseline must be 10/10 |
| Combined `passed` | Verdict match AND all compared fields match AND not a false CONFIRMED | Report per task and overall | Baseline 10/10 |
| False-CONFIRMED rate | Predictions of `CONFIRMED` when gold is not | **This is the headline.** Lower is better. 0 is the baseline | Baseline must be 0 |
| Catastrophic count | Same events, used as a raw count across 3 runs | Quote alongside the rate | 0 |
| Consistency | How often the same model flips across 3 runs of one task | Report; instability is itself a finding | n/a |

## Suite composition

| ID | Gold | Why it is in the suite |
| --- | --- | --- |
| T01_edited_amount | SUSPICIOUS | Digit edit on the screenshot, bank alert has the real amount |
| T02_reused_reference | SUSPICIOUS | Session ID already settled an older order |
| T03_wrong_beneficiary | SUSPICIOUS | Money went to a different person / bank |
| T04_datetime_mismatch | SUSPICIOUS | Same reference, date on the image was moved forward |
| T05_tampered_screenshot | SUSPICIOUS | Crop / font artifacts and no matching alert |
| T06_pending_as_success | UNVERIFIED | Status is PENDING |
| T07_pidgin_amount_2k5 | CONFIRMED | "2k5" means ₦2,500 and the alert agrees |
| T08_injection_hidden | SUSPICIOUS | Jailbreak text inside the narration, no alert |
| T09_clean_receipt | CONFIRMED | True-positive control |
| T10_reference_not_found | NOT_FOUND | Printed reference is absent from evidence |

Gold distribution: 6 SUSPICIOUS, 2 CONFIRMED, 1 UNVERIFIED, 1 NOT_FOUND. That mix stops a model from winning by always saying SUSPICIOUS or always saying CONFIRMED.

## Harness checks (already automated)

```
python -m pytest -q
```

Must show:

- every `reference_answer` passes
- every `decoy_answer` fails
- every non-CONFIRMED task has a catastrophic false-CONFIRMED decoy
- the baseline passes every task and never false-confirms
- the generator writes at least two valid PNGs
- `2k5` parses to 2500

## Model protocol

- 3 independent runs per task per model, temperature 0 unless a provider rejects that setting
- Save raw text, parsed JSON, and grader output
- Do not drop failed parses: they count as not passed (parsed fallback is `UNVERIFIED` with `parse_error: true`)
- Report free-tier models separately from GPT / Claude / Gemini so a cheap-model number is not mistaken for a frontier result

## What we will quote in the write-up

Lead with: "On N fake-or-unverified receipts, model M said CONFIRMED in X% of trials. The deterministic baseline said CONFIRMED in 0% of those cases." Then show the clean-receipt and pidgin controls so readers see the suite is not a trap.
