# AGENTS.md

Instructions for the coding agent (opencode / Cursor running Kimi) helping Timi build this micro1 eval on a weak Windows laptop.

## Who you are helping

Timi (Agoro Oluwatimilehin) is an AI/ML engineer in Lagos. Never call him a student. This is a solo project.

## Goal

Ship a rigorous, reproducible eval: "Can frontier AI tell a fake Nigerian bank-transfer receipt from a real one?" Judges reward **clear frontier-model failures**, a reliable grader, and a one-command rerun. They do not reward a product pitch.

## Security

- Never commit `.env`, API keys, or receipts that contain real customer data.
- Never paste secrets into chat, README, or commit messages.
- Use `.env.example` only in git. `.gitignore` already covers `.env`.
- Do not scrape real OPay / GTBank / Kuda / Moniepoint receipts. Generate fictional ones.
- Do not copy real bank logos, wordmarks, or UI assets. The generator already uses fictional brand names.

## PowerShell (this laptop)

Prefer `make.ps1` over bash. If you write a command, give the PowerShell form first.

```powershell
python -m venv .venv
.\venv\Scripts\Activate.ps1
# if execution policy blocks activation:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
pip install -r requirements.txt
python -m pytest -q
python -m generator.write_assets
python -m runner.run --backend baseline --runs 1
```

Older Windows PowerShell 5 may not support `&&`. Use `;` or separate lines. Do not assume WSL is installed. Do not add Docker or GPU dependencies.

## Build order

1. Keep the grader tests green. If you change gold labels, update `reference_answer` and `decoy_answer` in the same change and rerun `python -m pytest -q`.
2. Do not weaken the catastrophic false-CONFIRMED rule to lift a model's score.
3. Generate receipts with `python -m generator.write_assets` after any `image_spec` edit.
4. Run the baseline after task edits: it must stay at 10/10 with 0 false CONFIRMED. If it fails, fix the baseline or the gold, and write down why.
5. Only then call OpenRouter. Default to a free model while iterating. Frontier models (GPT, Claude, Gemini) are for the recorded submission runs, 3 trials each.
6. Save raw transcripts. Do not hand-edit them.
7. Fill `docs/failure_taxonomy.md` from those transcripts.
8. When zipping for HackerRank, exclude `.venv`, `.env`, `__pycache__`, videos, and anything that would push the archive over 50 MB.

## Grader contract

See `docs/grader_spec.md`. Short version:

- Exact verdict match required to pass
- Compared fields must match after normalisation
- Predicting `CONFIRMED` when gold is not `CONFIRMED` is catastrophic (score 0)
- Every task ships a reference answer (must pass) and a decoy (must fail)
- Pytest tests that contract. Do not delete those tests

## Style

- Python 3.10+, stdlib + Pillow + pytest. No extra web frameworks.
- Type hints on new public functions.
- Deterministic file order via `tasks/catalog.json`.
- Comments explain *why*, especially around Pidgin amounts and injection handling.

## Out of scope

Do not turn this repo into a full Sell-Safe clone, a web app, or a NEAR contract. TrustLock lives in a sibling folder and is a different hackathon.
