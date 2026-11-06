# Phase 4 progress log — 5 Nov 2026

## Harness state (all green)

- `python -m pytest -q` → 11 passed.
- Baseline: 10/10, 0 catastrophic false CONFIRMED.
- Receipts regenerated (10 PNGs in `assets/`).
- `results/latest_summary.json` still holds the baseline (a summary writes only on run completion).

## Runner changes (in `runner/run.py`, stdlib only)

- New direct backends: `--backend groq`, `--backend gemini`. OpenRouter stays primary.
- 15s pacing between live calls plus retry with backoff on 429 / 500 / 502 / 503 / 504.
- Gemini request carries an explicit `systemInstruction` with the full answer schema
  (first probe returned `{"confirmation": true}` without it).
- Keys come from local `.env` only, travel in headers, never appear in transcripts.
  `.env` is untracked; `.env.example` holds empty placeholders.

## Key status (lengths only, values never recorded)

- OPENROUTER, GROQ, GEMINI, META_MUSE keys present in local `.env`.
- Groq direct: HTTP 403 error 1010 — old key blocked on this network or restricted
  in its project dashboard. Code path works; key needs checking.
- Muse direct: not wired. Need the base URL, auth scheme, and model name from the
  old project's working code (not the key).

## Phase 4 status: BLOCKED on Gemini free-tier quota

- Gemini direct (`gemini-2.5-flash`), 3 runs/task = 30 calls needed.
- Saved 13/30 transcripts before quota cut in: T01 (3/3), T02 (3/3), T03 (3/3),
  T04 (3/3), T05 (1/3).
- Quota error: 429, `generate_content_free_tier_requests, limit: 20`.
- Partial tally: 3 passes, 0 catastrophic false CONFIRMED.
- Early finding (from transcripts, not memory): T01 passes as SUSPICIOUS;
  T02–T05 fail on off-schema verdicts (`REJECTED`, `Fraudulent`) instead of
  `SUSPICIOUS`. T09 clean receipt passes as CONFIRMED (post schema-instruction fix).
- OpenRouter free models were also rate-limited earlier (429s); one returned
  wrong-schema JSON (parse path handled it, scored 0.23, no false CONFIRMED).

## Resume commands (run from repo root, project `.venv`)

```powershell
# After Gemini quota resets:
.\.venv\Scripts\python.exe -m runner.run --backend gemini --model gemini-2.5-flash --runs 3
# Paid OpenRouter arm (costs real money, confirm model ID first):
.\.venv\Scripts\python.exe -m runner.run --backend openrouter --model <id> --runs 3
# Baseline re-check any time:
.\.venv\Scripts\python.exe -m runner.run --backend baseline --runs 1
```

## Still pending

- Finish Gemini 3-trial run after quota reset (22/30 saved).
- Claude arm replaced by Muse (see below); Groq still blocked on its key.
- Groq arm after its key is fixed, or Llama via OpenRouter.
- Fill `docs/failure_taxonomy.md` from full transcripts; update README numbers;
  record video; pack ZIP (per `docs/submission_checklist.md`).

## Claude arm attempt (5 Nov 2026, blocked, 0 transcripts)

- `anthropic/claude-sonnet-4` is retired on OpenRouter (404, no provider serves it).
  Current IDs include `anthropic/claude-sonnet-4.5`, `-4.6`, `-5`, `-opus-4.1+`, `-haiku-4.5+`.
- Single T09 probe with `anthropic/claude-sonnet-4.5` succeeded (verdict `APPROVED`,
  off-schema again, fields correct) — then the full `--runs 3` died on its first
  call with OpenRouter 402: only ~1966 tokens affordable. Credits are spent.
- Nothing was overwritten: the crash happened before any transcript write, so the
  GPT 3-trial summary (`results/summary-openrouter-20261105T203232Z.json`) and all
  30 GPT transcripts plus 13 Gemini transcripts are intact.
- To unblock: top up at https://openrouter.ai/settings/credits, then run
  `.\.venv\Scripts\python.exe -m runner.run --backend openrouter --model anthropic/claude-sonnet-4.5 --runs 3`.
  Update `docs/description_draft.md` if a different Claude ID is used.

## Gemini arm, second attempt (5 Nov 2026, blocked at 22/30)

- Quota reset, run relaunched, died at 22/30 with the same daily 429 (`limit: 20`).
- Saved tally: 22 transcripts, 3 passes (T01 3/3 only), 0 catastrophic.
- New verdict labels observed: T06 `DECLINED` once then `REJECTED`; T07 `LEGITIMATE`
  3/3; T08 `FRAUDULENT` on its single saved trial. Same pattern: fields right,
  labels off-schema.
- Root-cause fix applied per debugging triage: `_paced_call` in `runner/run.py`
  no longer retries 429s carrying the daily-cap marker (`limit: 20`) — retries
  only help per-minute limits and 5xx. Guard: `pytest` 11 passed after the change.
- Resume needs 8 more calls (T08 run2–run3, T09 ×3, T10 ×3) after the next reset.

## Muse vision arm, three trials (6 Nov 2026, `muse-spark-1.3`, `--runs 3`)

- Result: 6/30 passes, 0 false CONFIRMED. Model ID verified from local
  Sell-Safe config (`META_VISION_MODEL=muse-spark-1.3`); `muse-wonder-1.0`
  appears only in docs and was not used.
- Modality: vision — each call sends the receipt PNG plus the standard eval
  prompt. Passes: T01 3/3, T09 3/3. All other tasks 0/3.
- Headline finding: with the actual image in context, reasons are excellent
  (T02 cites the settled prior order and timestamp clash; T07 explains that
  '2k5' means NGN 2,500) but verdict labels stay off-schema: `invalid`,
  `mismatch`, `fraudulent`, `fabricated`, `fake`, `pending`, `legit`,
  `UNCONFIRMED`, `NOT_CONFIRMED`, `unconfirmed` — plus legal-but-wrong
  `UNVERIFIED` on T03/T04/T05. Judgment right, verdict contract failed.
- Sandbox DNS for `api.meta.ai` flaked twice mid-session (transient; probes
  passed between failures). Runner now retries transient network errors and
  empty responses, and fails fast on 401/402/403/404 and daily caps.
- This arm overwrote `results/latest_summary.json`; GPT 3-trial and baseline
  records live in their timestamped `results/summary-*.json` files.

## GPT arm, three trials (5 Nov 2026, `openai/gpt-4.1-mini`, `--runs 3`)

- Result: 6/30 passes, 0 catastrophic false CONFIRMED.
- Passes: T01 3/3 (edited amount → SUSPICIOUS), T09 3/3 (clean → CONFIRMED).
  All other tasks 0/3 with mean field scores 0.34–0.4.
- Headline finding: the model's fields and reasons are RIGHT on the failed
  tasks (it names the reused reference, the PENDING status, the 2,500 pidgin
  match) but its verdict labels are off-schema and consistent across trials:
  `rejected` (T02, T03, T05), `not_confirmed` (T06), `valid` (T07),
  `discrepancy_detected` once (T04), `UNVERIFIED` instead of SUSPICIOUS (T08),
  `unconfirmed` instead of NOT_FOUND (T10). Judgment passes; the verdict
  contract fails. See `results/transcripts/*__openrouter__run*.json`.
- Consistency note: identical wrong labels across all 3 trials — systematic,
  not sampling noise.
- Runner fixes that enabled this arm: `max_tokens: 2000` on OpenRouter/Groq
  (was reserving 65k tokens per call → 402 on low credits) and the explicit
  answer-schema system prompt (was returning `{"confirmation": true}`).
- Note: this arm overwrote `results/latest_summary.json`; the baseline 10/10
  record lives in `results/summary-baseline-20261105T193929Z.json`.
