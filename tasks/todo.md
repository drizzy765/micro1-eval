# Unfinished tasks — micro1 eval (tracked here, see `tasks/plan.md`)

## Task 1: Finish Gemini 3-trial arm after quota reset — DONE (8 Nov 2026)

**Description:** Run the remaining 8 Gemini calls (T08 run2–run3, T09 x3, T10 x3) after a full daily reset so the arm reaches 30/30. Done 8 Nov: 8/8 landed first try, no pre-probe, combined 6/30 (T01+T09 3/3), 0 false CONFIRMED over 24 negatives.

**Acceptance criteria:**
- [x] `results/runs/gemini-gemini-2.5-flash-20261108T172302Z/` holds the 8 new trial JSONs, old 22 intact
- [x] Timestamped `results/summary-gemini-gemini-2.5-flash-20261108T172302Z.json` records 30 trials, 6 passes, 0 false CONFIRMED over completed negatives
- [x] `results/audit-20261108-gemini-complete.json` written for the completed arm

**Verification:**
- [x] Tests pass: `python -m pytest -q`
- [x] Baseline succeeds: `python -m runner.run --backend baseline --runs 1`
- [x] Manual check: count trial files per task (T08–T10 show 3 each), confirm no overwrite of prior run dir

**Dependencies:** None (was blocked on quota clock — 7 Nov attempt: probe + 20 landed, died on `limit: 20`; 8 Nov reset cleared it)

**Files likely touched:**
- `results/runs/gemini-gemini-2.5-flash-<stamp>/`
- `results/summary-gemini-*.json`
- `results/audit-*.json`

**Estimated scope:** Small: 1-2 files plus generated run dir

## Task 2: ~~Finish Claude arm~~ — DROPPED (user decision, 7 Nov 2026)

**Description:** Claude arm removed from scope — OpenRouter credits cannot cover it (7 Nov probe: `OpenRouter HTTP 402: ... can only afford 1764` of 2000 tokens). 0 Claude transcripts exist; nothing to preserve. Frontier coverage rests on GPT-4.1-mini, Muse Spark vision, GLM 5.3 Flash, and the partial Gemini arm.

**Acceptance criteria:**
- [x] All Claude references in plan, checklist, description, README, and eval report updated to dropped status
- [x] No Claude arm expected by any quality gate

**Verification:**
- [x] `grep -r Claude` shows only historical/dropped notes, no open Claude tasks

**Dependencies:** None (dropped; was blocked on credits. Groq re-probed 8 Nov: still HTTP 403 error 1010, stays dropped.)

**Files touched:** plan/checklist/description/README/eval-report (docs only)

**Estimated scope:** XS: docs only, 0 trials

## Task 3: Resolve Groq/Llama scope and `results/runs/` gitignore

**Description:** Decide the Groq/Llama arm fate and stop untracked run dirs from polluting `git status`.

**Acceptance criteria:**
- [x] Either Groq key fixed with one passing probe, or arm explicitly dropped and noted in `reports/eval-report.md` limitations
- [x] `.gitignore` decision recorded: `results/runs/` ignored or committed
- [x] `git status --short` no longer shows surprise untracked run dirs

**Verification:**
- [x] Tests pass: `python -m pytest -q` (14 passed, 8 Nov)
- [x] Manual check: `git status --short` clean of run dirs (runs/ + transcripts/ gitignored; 8 Nov confirmed)

**Dependencies:** None

**Files likely touched:**
- `.gitignore`
- `reports/eval-report.md`
- `reports/phase4_progress.md`

**Estimated scope:** Small: 1-2 files

## Checkpoint: Frontier runs

- [x] All attempted arms have timestamped summaries plus unique run dirs (Gemini completed 8 Nov: 4 full arms × 30 + baseline)
- [x] `python -m pytest -q` green (expect 14 passed incl. `tests/test_run_dirs.py`)
- [x] Baseline still 10/10, 0 false CONFIRMED
- [ ] Review with human before building ZIP

## Task 4: Finalize HackerRank description from audit numbers

**Description:** Replace the placeholder frontier sentence in the description draft with audited false-CONFIRMED rates and trim to the form limit. Done 7 Nov: short version cites baseline 10/10, GPT/Muse/GLM 6/30 each, 0 false CONFIRMED, Gemini 3/22 partial; synthetic + fictional-brands stated; verified at exactly 900 chars.

**Acceptance criteria:**
- [x] `docs/description_draft.md` short version cites real pass and false-CONFIRMED tallies from the audit file
- [x] Text states synthetic data, fictional brands, no real logos
- [x] Length fits HackerRank form (short 900 chars, longer variant kept separately)

**Verification:**
- [x] Counted by script: 900 chars (header claim corroborated, not asserted)
- [x] Modality split noted in longer variant (text-input vs vision); short version names Muse Spark vision arm

**Dependencies:** Tasks 1-2 (numbers final)

**Files likely touched:**
- `docs/description_draft.md`

**Estimated scope:** XS: 1 file

## Task 5: Record and upload walkthrough video

**Description:** Record the 3–5 minute walkthrough per `docs/video_script.md` with real numbers, upload unlisted, keep the file out of the ZIP.

**Acceptance criteria:**
- [ ] Video follows `docs/video_script.md` beats and hard-stops by 5:00
- [ ] On-screen numbers match the audit file; limitations beat included
- [ ] Link is watchable without a login wall (unlisted YouTube or anyone-with-link Drive)

**Verification:**
- [ ] Manual check: play link in a logged-out window, audio intelligible, charts legible
- [ ] Manual check: no secrets or real customer data on screen

**Dependencies:** Tasks 1-2 (for final numbers)

**Files likely touched:**
- (no repo files; link recorded alongside Task 7 confirmation)

**Estimated scope:** XS: 0 repo files

## Task 6: Build and verify submission ZIP under 50 MB — DONE (8 Nov 2026)

**Description:** Stage a clean tree and pack code-only ZIP per `docs/submission_checklist.md`. Built `micro1-receipt-eval-submit.zip` (83 entries, 562,911 bytes) from a staged tree; includes the new diagnostic script + JSON, appendix, cleanroom log, and completed Gemini numbers.

**Acceptance criteria:**
- [x] ZIP contains tasks, generator, grader, runner, baseline, tests, docs, assets PNGs, requirements, make files, `.env.example`, `.gitignore`, summary JSON and report tables
- [x] ZIP excludes `.venv/`, `.env`, `__pycache__/`, `.pytest_cache/`, run dirs, transcripts, videos, `*.mp4`
- [x] `Length` 562911 < 52428800 and no API keys found in staged copy (pattern grep clean)

**Verification:**
- [x] Tests pass on clean checkout: `python -m pytest -q` (14 passed, fresh venv /tmp, no keys)
- [x] Baseline succeeds: `python -m runner.run --backend baseline --runs 1` (10/10, per-file task hashes identical)
- [x] Manual check: ZIP size and forbidden-entry scan clean (`.gitignore` flagged by naive grep only — it is required contents)

**Dependencies:** Tasks 1-4 (final numbers and docs in ZIP)

**Files likely touched:**
- (build artifact only: `micro1-receipt-eval-submit.zip` plus TEMP stage dir)

**Estimated scope:** Small: 0 tracked files, 1 artifact

## Task 7: Eligibility re-check and HackerRank submit

**Description:** Re-read both event pages the morning of submit, confirm eligibility, submit once, save proof.

**Acceptance criteria:**
- [ ] HackerRank event and Luma pages re-read same day; 2-year experience line adjudicated
- [ ] Single HackerRank submit: ZIP plus video link plus description; Participant Agreement accepted
- [ ] Confirmation receipt saved outside the ZIP

**Verification:**
- [ ] Manual check: confirmation file exists and names what went into the ZIP (freeze golds after this point)

**Dependencies:** Task 6

**Files likely touched:**
- (confirmation saved outside repo or in `reports/` only if it contains no secrets)

**Estimated scope:** XS: 0-1 files

## Checkpoint: Complete

- [ ] All acceptance criteria above met
- [ ] Quality bar in `docs/submission_checklist.md` all checked
- [ ] Ready for review; winners due 23 Nov 2026 — no gold edits post-submit without snapshot
