# Phase 4 progress log — 5 Nov 2026 (provenance cleanup 6 Nov, no reruns)

## Harness state (all green)

- `python -m pytest -q` → 14 passed (incl. `tests/test_run_dirs.py`).
- Baseline: 10/10, 0 catastrophic false CONFIRMED.
- Receipts regenerated (10 PNGs in `assets/`).
- `results/latest_summary.json` always points at the most recent completed arm;
  every arm also keeps a timestamped `results/summary-*.json`.

## Runner changes (in `runner/run.py`, stdlib only)

- New direct backends: `--backend groq`, `--backend gemini`. OpenRouter stays primary.
- 15s pacing between live calls plus retry with backoff on 429 and 5xx; fail
  fast on spent daily caps (`limit: 20`), 401/402/403/404, and retry transient
  empty responses.
- Gemini request carries an explicit `systemInstruction` with the full answer schema
  (first probe returned `{"confirmation": true}` without it).
- `--backend muse` (vision: PNG + prompt) and `--backend nvidia` (vision) added later;
  see arm sections below.
- Provenance: every `run_eval` writes transcripts to a unique
  `results/runs/<backend>-<model>-<stamp>/` directory and never reuses a
  non-empty one (regression-tested in `tests/test_run_dirs.py`); the summary
  records `run_id` and `run_dir`.
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

- Finish Gemini 3-trial run after quota reset (22/30 saved; transcripts intact).
- Claude arm replaced by Muse (0 Claude transcripts; see below).
- Groq arm after its key is fixed, or Llama via OpenRouter.
- `results/runs/` collision guard is in place, but `results/runs/` is not yet
  in `.gitignore` — untracked run directories will show in `git status`;
  decide whether to ignore or commit them.
- Fill `docs/failure_taxonomy.md` from preserved transcripts only (GPT
  excluded); update README numbers; record video; pack ZIP
  (per `docs/submission_checklist.md`).

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

## NVIDIA direct probe (6 Nov 2026, `deepseek-ai/deepseek-v4.1-flash`, vision) — NO COMPLETED CALLS

- Backend `--backend nvidia` added (stdlib, prompt + PNG, max_tokens 2000,
  temp 0.0; refuses text-only if the image is missing).
- Two T09 probes read-timed-out at 120s and 180s. Zero evaluation calls
  completed, zero counted. A timeout establishes nothing further: it does not
  prove auth was accepted, and it does not prove the model itself was
  unavailable (network path, gateway queuing, and model latency are all still
  on the table).
- Per instruction, fell back to `z-ai/glm-5.3-flash` as a separately labelled
  arm (OpenRouter backend, transcribed-fields modality — labelled by exact
  model ID in every transcript and summary, no silent switch).

## GLM arm, three trials (6 Nov 2026, `z-ai/glm-5.3-flash` via OpenRouter, TEXT input)

- Result: 6/30 exact-schema passes, 0 false CONFIRMED over 24 completed
  negative-case trials (0/24). Passes: T01 3/3, T09 3/3.
- Input-modality warning: this arm received transcribed receipt fields
  (text), not receipt images. Compare it only with the other text-input arm
  (GPT); the vision arm (Muse) had different inputs and belongs in a separate
  comparison.
- On failed trials the verdict labels were off-schema and unstable across
  trials: `REJECTED`, `FAIL`, `fraudulent`, `unverifiable`, `rejected`,
  `unconfirmed`, `NOT_CONFIRMED`, `verified`, `GENUINE`, `VERIFIED`,
  `not_confirmed`. Sampled raw outputs (T02, T07 run 1) show extracted amounts
  and reasons consistent with the gold evidence, but fields/reasons alone do
  not establish verdict correctness — see the semantic-correctness note in
  Provenance and limitations.
- Settings: existing prompt unchanged, temperature 0.0, max_tokens 2000.
  No prompt tuning performed against these tasks, and no label remapping was
  introduced: the strict grader scores exactly what each model emitted.
- Data note: transcript files were keyed `{task}__{backend}__run{n}.json`
  (backend only, no model), so this arm overwrote the 30 GPT trial-level
  transcript files. GPT aggregates survive intact in
  `results/summary-openrouter-20261105T203232Z.json` (see GPT section).
  All future runs write to unique `results/runs/<backend>-<model>-<stamp>/`
  directories (regression-tested), so this cannot recur.

## Muse vision arm, three trials (6 Nov 2026, `muse-spark-1.3`, VISION input)

- Result: 6/30 exact-schema passes, 0 false CONFIRMED over 24 completed
  negative-case trials (0/24). Model ID verified from local
  Sell-Safe config (`META_VISION_MODEL=muse-spark-1.3`); `muse-wonder-1.0`
  appears only in docs and was not used.
- Modality: vision — each call sends the receipt PNG plus the standard eval
  prompt. Passes: T01 3/3, T09 3/3. All other tasks 0/3. Keep this arm in a
  separate comparison from the text-input arms (GPT, GLM): inputs differed.
- On failed trials the verdict labels were off-schema: `invalid`, `mismatch`,
  `fraudulent`, `fabricated`, `fake`, `pending`, `legit`, `UNCONFIRMED`,
  `NOT_CONFIRMED`, `unconfirmed` — plus legal-but-wrong `UNVERIFIED` on
  T03/T04/T05. Sampled raw outputs (T02, T07 run 1) show reasons that track the
  gold evidence (settled prior order and timestamp clash; '2k5' = NGN 2,500),
  but that is a qualitative observation, not a correctness metric — see
  Provenance and limitations.
- Sandbox DNS for `api.meta.ai` flaked twice mid-session (transient; probes
  passed between failures). Runner now retries transient network errors and
  empty responses, and fails fast on 401/402/403/404 and daily caps.
- This arm overwrote `results/latest_summary.json`; GPT 3-trial and baseline
  records live in their timestamped `results/summary-*.json` files.

## GPT arm, three trials (5 Nov 2026, `openai/gpt-4.1-mini` via OpenRouter, TEXT input) — AGGREGATE-ONLY

- Result: 6/30 exact-schema passes, 0 false CONFIRMED over 24 completed
  negative-case trials (0/24). Passes: T01 3/3, T09 3/3.
- Provenance warning: this arm's 30 trial-level transcript files were
  overwritten by the later GLM arm (old backend-only file keying) and are
  unrecoverable — never committed (git-ignored), no stash, no backups, and raw
  responses are never reconstructed from aggregates. What survives is the
  timestamped summary (`results/summary-openrouter-20261105T203232Z.json`):
  per-task passes, mean scores, catastrophic counts. Quote those tallies only.
- Therefore GPT is EXCLUDED from transcript-based analysis (no per-trial
  verdict-label claims, no reason-quote claims). The label lists recorded
  during the live run are dropped as unverifiable.
- Runner fixes that enabled this arm: `max_tokens: 2000` on OpenRouter/Groq
  (was reserving 65k tokens per call → 402 on low credits) and the explicit
  answer-schema system prompt (was returning `{"confirmation": true}`).
- Note: this arm overwrote `results/latest_summary.json`; the baseline 10/10
  record lives in `results/summary-baseline-20261105T193929Z.json`.

## Provenance and limitations (read before quoting numbers)

- Exact-schema pass rate is the only correctness metric: verdict match AND all
  compared fields match under the strict grader. No label remapping exists or
  will be added to flatter a model.
- Semantic verdict correctness is NOT established by correct fields or good
  reasons. A model can extract every amount and still fail the verdict
  contract; that is the finding, not a near-pass.
- False CONFIRMED is reported against completed negative-case trials only
  (gold verdict is not CONFIRMED): baseline 0/8, GPT 0/24, Muse 0/24, GLM 0/24,
  Gemini partial 0/19 (22 saved trials, T07 ×3 excluded). Quota errors, parse
  failures, and timeouts are transport problems, never counted as answers.
- Zero observed false CONFIRMED is an observation at this sample size, not
  proof of zero risk. No arm exceeds 30 trials.
- Historical summaries are byte-for-byte unchanged; `results/latest_summary.json`
  is a pointer that each completed arm legitimately overwrites.
- No prompt was tuned against these tasks and no arm was rerun to lift its
  score. The Gemini arm is incomplete (22/30); its numbers are partial.
- GPT is aggregate-only (see above): tallies citable, wording not.

## Gemini arm, third attempt (6 Nov 2026, probe passed, run died fast)

- One T09 probe passed (`CONFIRMED`, 1.0), then the full run died on the daily
  cap almost immediately — fail-fast worked, only ~2 quota calls burned.
- 22 legacy transcripts intact; 1 new trial saved in its own run dir
  (`results/runs/gemini-gemini-2.5-flash-20261106T204918Z/`, T01 run 1,
  SUSPICIOUS, passed). Unique-dir routing held: no overwrites.
- Lesson: a passing probe does not imply arm capacity on a ~20/day cap.
  Next attempt should wait for a fuller reset (next day), not minutes.
