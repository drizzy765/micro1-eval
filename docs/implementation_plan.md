# Implementation plan — micro1 Eval Hackathon

Target submit: **7 November 2026** (hard deadline 8 November 2026, 9:15 PM PST).  
This is a solo entry.

micro1 is a pivot from "Sell-Safe succeeds" to **"frontier models still cannot reliably tell a fake Nigerian transfer receipt from a real one."** Sell-Safe's deterministic engine is the 0% false-CONFIRMED baseline, not the product being judged.

## Day 0 — Wednesday 5 November (today)

Already in this repo:

- [x] 10 fully specified tasks in `tasks/`
- [x] Deterministic grader with reference-pass / decoy-fail tests
- [x] Receipt generator (all 10 styles render; tests cover at least 2)
- [x] Baseline engine that scores 10/10
- [x] Runner skeleton (baseline + OpenRouter)
- [x] Docs, skills, Makefile / make.ps1

Timi still does today:

1. Read `docs/task_spec.md` and `docs/grader_spec.md` end to end.
2. Run `make.ps1 setup`, `make.ps1 test`, `make.ps1 baseline` on the Windows laptop.
3. Confirm the Luma eligibility note (see `docs/submission_checklist.md`): Luma says "at least two years of professional experience." The HackerRank page lists expertise + coding skill and does not repeat that sentence. Read both pages before sinking more time.
4. Copy `.env.example` to `.env` and add an OpenRouter key. Do not commit it.
5. Smoke-test one cheap/free OpenRouter model on 2 tasks to confirm the runner parses JSON.

## Day 1 — Thursday 6 November

1. Generate all receipt PNGs: `python -m generator.write_assets`.
2. Run 3 trials each on at least one free model (build) and start the frontier set:
   - GPT (OpenAI, via OpenRouter)
   - Claude (Anthropic)
   - Gemini (Google)
3. Save every raw transcript in its run directory under `results/runs/`
   (the runner creates `<backend>-<model>-<stamp>/` and refuses to overwrite).
4. Fill `docs/failure_taxonomy.md` from the actual transcripts. Quote the model, do not paraphrase away the mistake.
5. Add charts in `reports/` (pass rate by task, false-CONFIRMED rate by model, confusion-style table). A simple matplotlib or even a hand-built markdown table is fine; the laptop is weak, skip heavyweight notebooks.
6. If a task is ambiguous (two reasonable golds), fix the gold and the prompt. Re-run the grader tests. Never silently change a gold to make a model look worse.

## Day 2 — Friday 7 November (submit)

1. Finish frontier runs (3 per task per model).
2. Write the README "Results" section from `results/latest_summary.json` — numbers first, then *why* the failures matter for Instagram sellers.
3. Record the 3–5 minute walkthrough using `docs/video_script.md`. Upload to YouTube unlisted (or Drive with "anyone with the link"). Do not put the video inside the ZIP.
4. Write the short description from `docs/description_draft.md`.
5. Build the submission ZIP of **code only**, max 50 MB:
   - Include tasks, generator, grader, runner, baseline, tests, docs, skills, requirements, make.ps1, assets PNGs, the summary JSON.
   - Exclude `.venv/`, `.env`, `__pycache__`, videos, and anything over a few MB that a judge does not need.
6. Submit once on HackerRank: ZIP + video link + description. Accept the Participant Agreement.

## What we are cutting (on purpose)

- 50+ real customer receipts (confidential-data risk, too slow)
- Live Instagram chat eval and Muse vision bake-off
- A calibration / confidence score besides the four verdicts
- Multi-author submissions (not allowed)

## Risks

| Risk | What to do |
| --- | --- |
| OpenRouter rate limits or a paid-model bill | Build on free models; run frontier last; keep `--runs 3` only for the final pass |
| A frontier model actually passes everything | That is an honest result. Dig into qualitative errors (wrong reasons, brittle field parsing). If needed, add one harder sibling task — do not invent gotchas |
| Laptop too slow for image work | Receipts are already cheap PIL images. Do not add ML-based image attackers |
| ZIP over 50 MB | Assets are small PNGs; the usual culprit is `.venv`. Always zip from a clean tree |
