# Submission checklist — micro1 Eval Hackathon

Official pages (read again the morning you submit):

- HackerRank event: https://www.hackerrank.com/event/micro1-eval-hackathon
- Luma page: https://luma.com/dtlqzj01

Deadline: **8 November 2026, 9:15 PM PST**. Target send: **7 November**.

## Eligibility — verify before you spend the weekend

- This is a solo entry.
- HackerRank lists required expertise (coding, AI tools, ability to design evals) and a Participant Agreement.
- **Luma says the event is "open to experts with at least two years of professional experience."** The HackerRank page text we fetched does not repeat that sentence. Read both pages, and the agreement, before submitting. If the 2-year line is enforced and you are unsure you qualify, do not submit.
- Registration on Luma is not the same as entering on HackerRank. Enter on HackerRank.

## What you upload

1. **One ZIP of code**, maximum **50 MB**. No video inside the ZIP.
2. **A link** to a short video walkthrough (unlisted YouTube or a public Drive link).
3. **A short description** (use `docs/description_draft.md`).

## ZIP contents (include)

- `README.md` with the one-command rerun and the final numbers
- `tasks/` (all ten JSON files + `catalog.json`)
- `generator/`, `grader/`, `runner/`, `baseline/`, `tests/`
- `docs/`
- `assets/` PNGs (small)
- `requirements.txt`, `Makefile`, `make.ps1`, `.env.example`, `.gitignore`
- `results/latest_summary.json` and the public report tables
- `skills/` if it still fits comfortably

## ZIP contents (exclude)

- `.venv/`
- `.env` (secrets)
- `__pycache__/`, `.pytest_cache/`
- Video files, raw screen recordings, `.mp4`
- Anything that would push the archive over 50 MB
- Real customer receipts or private Sell-Safe dumps

Suggested PowerShell pack (from the repo root, after tests pass):

```powershell
$exclude = @('.venv', '.env', '__pycache__', '.pytest_cache', '.git')
# Use Compress-Archive on a staged copy so .venv does not sneak in:
$stage = Join-Path $env:TEMP 'micro1-submit'
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item $stage -ItemType Directory | Out-Null
robocopy . $stage /E /XD .venv .git __pycache__ .pytest_cache results\transcripts /XF .env *.mp4
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath .\micro1-receipt-eval-submit.zip -Force
Get-Item .\micro1-receipt-eval-submit.zip | Select-Object Name, Length
```

Confirm the ZIP is under 50 MB (`Length` < 52428800).

## Quality bar before you click submit

- [ ] `python -m pytest -q` → 11 passed
- [ ] Baseline: 10/10, 0 false CONFIRMED
- [ ] Frontier runs exist: GPT, Muse, GLM, 3 trials each (+ Gemini partial); Claude dropped 7 Nov (cost)
- [ ] `docs/failure_taxonomy.md` filled from transcripts, not from memory
- [ ] README quotes the headline false-CONFIRMED rates
- [ ] Video follows `docs/video_script.md` and is watchable without a login wall
- [ ] Description is honest: synthetic data, fictional brands, no real logos
- [ ] No API keys anywhere in the ZIP
- [ ] You opened HackerRank and Luma today and still believe you are eligible

## After submit

Save the HackerRank confirmation. Winners are due **23 November 2026**. Do not edit the public task golds after you submit without keeping a snapshot of what went into the ZIP.
