# Implementation Plan: Finish micro1 Eval Submission

## Overview
Finish the remaining eval work for the 7 Nov 2026 target (hard deadline 8 Nov 9:15 PM PST): complete the blocked Gemini arm (8/30 calls left), resolve housekeeping, then finalize description, video, ZIP, and HackerRank submit. Claude arm dropped 7 Nov (user decision — OpenRouter credits unaffordable). Provenance rules hold throughout: no label remapping, no transcript hand-edits, text-input vs vision arms compared separately.

## Architecture Decisions
- Strict grader stays unchanged; exact verdict match is the only correctness metric.
- No prompt tuning against tasks to lift scores; temperature 0.0, existing prompt unchanged.
- GPT stays aggregate-only (trial transcripts lost to old backend-only file keying, now fixed with unique `results/runs/<backend>-<model>-<stamp>/` dirs). Quote tallies only.
- Text-input arms (GPT, GLM, Gemini) and vision arm (Muse Spark 1.3) compared separately.
- False CONFIRMED denominators use completed negative-case trials only; quota errors, parse failures, timeouts are transport, never answers.

## Task List

### Phase 1: Frontier runs completion
- [ ] Task 1: Finish Gemini 3-trial arm after quota reset
- [x] Task 2: DROPPED — Claude arm removed (cost, user decision 7 Nov)
- [ ] Task 3: Resolve Groq/Llama scope and `results/runs/` gitignore

### Checkpoint: Frontier runs
- [ ] All attempted arms have timestamped summaries plus unique run dirs
- [ ] `python -m pytest -q` green
- [ ] Baseline still 10/10, 0 false CONFIRMED

### Phase 2: Submission pack
- [x] Task 4: Finalize HackerRank description from audit numbers (done 7 Nov, 900 chars)
- [ ] Task 5: Record and upload walkthrough video
- [ ] Task 6: Build and verify submission ZIP under 50 MB
- [ ] Task 7: Eligibility re-check and HackerRank submit

### Checkpoint: Complete
- [ ] Quality bar in `docs/submission_checklist.md` all checked
- [ ] HackerRank confirmation saved
- [ ] No golds edited post-submit without snapshot

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Gemini daily cap (`limit: 20`) hits again | Med | Wait for full next-day reset, not minutes; fail-fast guard already in `runner/run.py` avoids burning quota |
| OpenRouter credits spent (402 seen) | High | Claude arm dropped 7 Nov (unaffordable); no Claude spend planned |
| Groq 403 / NVIDIA timeouts recur | Low | Drop the arm explicitly and document as excluded; do not count timeouts as answers |
| ZIP over 50 MB | Med | Stage a clean copy, exclude `.venv .git __pycache__ .pytest_cache results/transcripts`, check `Length` < 52428800 |
| Accidental secret in ZIP | High | Pack from staged copy; grep stage for keys before `Compress-Archive` |

## Open Questions
- Is Groq key fixable, or is Llama via OpenRouter the replacement? If neither, drop and note in eval report limitations.
- Should `results/runs/` be gitignored or committed? Currently untracked run dirs show in `git status`.
- ~~Which exact Claude model ID goes in the description~~ — moot: Claude dropped 7 Nov.

## Parallelization Opportunities
- Safe to parallelize: Task 4 (description) with Task 5 prep (script review) while waiting on quota reset.
- Must be sequential: Task 1 and Task 2 runs before Task 4 numbers and Task 6 ZIP contents; Task 6 before Task 7.
- Needs coordination: README/audit numbers and description must all cite `results/audit-20261106.json` successor, not `latest_summary.json` alone (pointer file overwrites per arm).
