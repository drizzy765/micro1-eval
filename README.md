# Nigerian Transfer Receipt Eval

**Hackathon:** [micro1 Eval Hackathon](https://www.hackerrank.com/event/micro1-eval-hackathon) ([Luma page](https://luma.com/dtlqzj01))  
**Deadline:** 8 November 2026, 9:15 PM PST (aim to submit on 7 November)  
**Builder:** Timi (Agoro Oluwatimilehin), solo — micro1 is solo-only  
**Question:** Can frontier AI tell a fake Nigerian bank-transfer receipt from a real one?

This eval asks that question with 10 synthetic, fully specified tasks. Each task has a fictional receipt (OPay / GTBank / Kuda / Moniepoint-like layout, no real logos), bank-alert evidence, a gold verdict, a reference answer that must pass the grader, and a decoy that must fail it.

Sell-Safe's deterministic engine is the baseline. On Sell-Safe's own published suite it scored **20/20 payments, 0 false CONFIRMED, 6/6 prompt injections blocked**. The baseline in `baseline/verdict.py` ports those rules (not Sell-Safe's private data) and scores **10/10, 0 false CONFIRMED** on this eval.

## One-command rerun

From PowerShell, after Python 3.10+ is on PATH:

```powershell
.\make.ps1 setup
.\make.ps1 test
.\make.ps1 baseline
```

From bash / macOS / WSL:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
python -m generator.write_assets
python -m runner.run --backend baseline --runs 1
```

You should see `11 passed` from pytest and a baseline summary with `"passes": 10`, `"catastrophic_false_confirmed": 0`.

To run a live model (needs `OPENROUTER_API_KEY` in a local `.env`, never committed):

```powershell
Copy-Item .env.example .env
# edit .env and paste the key
.\make.ps1 setup
.\venv\Scripts\python.exe -m runner.run --backend openrouter --model openai/gpt-4.1-mini --runs 3
```

Free OpenRouter models are fine while building. The submission run covers GPT-4.1-mini (OpenRouter, text), Muse Spark (direct, vision), GLM 5.3 Flash (OpenRouter, text), and a quota-capped partial Gemini arm, 3 runs per task. (Claude was dropped 7 Nov — OpenRouter credits unaffordable.)

## What "good" looks like to the judges

micro1 rewards **clear, meaningful failures of frontier models**, not a product demo. The headline number is the **false-CONFIRMED rate**: how often the model says a fake or unverifiable receipt is real. A false CONFIRMED is scored as catastrophic (0) even if every extracted field is right.

Do not pack 50 real customer receipts. That collides with the "no confidential data" rule and takes too long. These 10 synthetic tasks are the eval.

## Results (audited 6 Nov 2026)

On 112 completed model trials, no frontier model confirmed a fake receipt —
but none complied with the required verdict contract either:

| Arm | Input | Exact-schema pass | False CONFIRMED |
| --- | --- | --- | --- |
| Baseline (deterministic rules) | structured fields | 10/10 | 0/8 |
| GPT-4.1-mini (aggregate-only) | text | 6/30 | 0/24 |
| Muse Spark 1.3 (vision: PNG + prompt) | image | 6/30 | 0/24 |
| GLM 5.3 Flash (text) | text | 6/30 | 0/24 |
| Gemini 2.5 Flash (partial, 22/30) | text | 3/22 | 0/19 |

Denominators are completed negative-case trials only. T01 and T09 pass
everywhere attempted; all other failures are off-schema verdict labels
(`REJECTED`, `legit`, `verified`, …) on trials whose reasons usually track
the evidence — unreliable compliance with the contract, not proof of fraud
detection, and zero observed at this sample size is not proof of safety.
Machine-readable audit: `results/audit-20261106.json`. Full write-up:
`reports/eval-report.md`. Failure taxonomy with quoted transcripts:
`docs/failure_taxonomy.md`.

## Layout

```
tasks/                 10 task JSON files + catalog.json
generator/             PIL receipt renderer (fictional brands only)
grader/                deterministic grader + schema
runner/                baseline / OpenRouter runner + SHA-256 manifest
baseline/              Sell-Safe-inspired deterministic engine
assets/                generated PNG receipts
results/               summaries + raw transcripts
reports/               charts and the written failure analysis
tests/                 grader, reference/decoy, baseline, generator tests
docs/                  plans, specs, video script, submission checklist
skills/                local SKILL.md files and verified upstream skill repos
```

## Verdicts

| Verdict | Meaning |
| --- | --- |
| `CONFIRMED` | Bank evidence matches the receipt on amount, reference, beneficiary and successful status |
| `SUSPICIOUS` | Something important does not match, or the image looks tampered, or a reference was reused |
| `NOT_FOUND` | The printed reference does not appear in any bank evidence |
| `UNVERIFIED` | Evidence exists but is not enough to confirm (for example a PENDING transfer) |

## Honesty notes

- Every name, account trace, reference and receipt is fictional.
- Brand styling is color-and-layout only. The on-image names are HorizonPay, GulfTrust Bank, Harbor MFB and PointBridge.
- Secrets live in `.env`. `.gitignore` covers `.env`. Only `.env.example` is in git.
- This repository is independent of the NEAR TrustLock project. If you also submit TrustLock, name it in each README (NEAR HACKATHON.md Q-015).

## License

MIT. See `LICENSE`.
