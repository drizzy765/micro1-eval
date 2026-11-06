# ADR-001: Direct Groq/Gemini fallback backends in the runner

## Status
Accepted

## Date
2026-11-05

## Context
The runner only spoke to models through OpenRouter. When OpenRouter free-tier
models rate-limit (observed HTTP 429s), model runs stop entirely. Timi holds
usable API keys from old projects (Groq, Gemini, Meta Muse), so direct
fallbacks remove the single-provider bottleneck during the submission window.

Constraints: Python stdlib + Pillow + pytest only (see `AGENTS.md`), secrets
stay in local `.env` and out of git and transcripts, and the grader contract
plus transcript schema must not change.

## Decision
Add `--backend groq` and `--backend gemini` to `runner/run.py` as direct,
stdlib-`urllib`-only callers. OpenRouter stays the primary backend. Muse
direct is deferred until the base URL, auth scheme, and model name are known
from the old project's working code (the key alone is not enough to wire it).

Hardening in the same change: API keys from env only (never CLI), keys in
request headers (Gemini key uses `x-goog-api-key` so it never lands in a URL),
Gemini model IDs allowlisted before URL interpolation, 15s pacing between
live calls, and retry with backoff on 429/500/502/503/504.

## Alternatives Considered

### OpenRouter only, retry and wait out limits
- Pros: no code change, one transcript path.
- Cons: a single provider outage or quota block stops all frontier arms at once.
- Rejected: fallback costs little (same prompt builder, same schema, same grader).

### Add provider SDKs (google-generativeai, groq, meta clients)
- Pros: richer client features.
- Cons: new pip deps on a weak laptop, more failure modes, conflicts with the
  stdlib-only repo rule.
- Rejected: plain HTTPS calls cover everything the eval needs.

### Auto-failover inside one run (try OpenRouter, fall back mid-run)
- Pros: runs self-heal.
- Cons: mixed-backend transcripts inside one summary muddy the write-up.
- Rejected: one backend per run; the operator switches backends explicitly.

## Consequences
- `python -m runner.run --backend groq|gemini|muse` works with the same prompt,
  transcript, summary, and SHA-manifest flow as OpenRouter.
- `--backend muse` (added 6 Nov 2026) sends the receipt PNG plus the standard
  prompt (vision). Verified runtime model is `muse-spark-1.3` from local
  Sell-Safe `META_VISION_MODEL`; `muse-wonder-1.0` is docs-only and unused.
  First full arm: 6/30, 0 false CONFIRMED.
- `.env.example` gains empty `GROQ_API_KEY`, `GEMINI_API_KEY`,
  `META_MUSE_API_KEY` placeholders. Real keys live only in local `.env`.
- Gemini needed an explicit `systemInstruction` carrying the answer schema:
  without it the model returned `{"confirmation": true}` on T09.
- Known issue logged in `reports/phase4_progress.md`: the old Groq key hits
  HTTP 403 error 1010 (blocked or restricted); Gemini free tier caps at ~20
  requests/day, which paused the 30-call Phase 4 run at 13/30 transcripts.
