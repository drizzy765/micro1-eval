"""Post-hoc semantic-vs-format diagnostic (disclosure only, never a rescore).

Reads intact trial transcripts plus task prompts and reports three tables:

1. Failure split per arm: pure-label (all compared fields correct) vs
   field-error vs parse-fallback. A pure-label failure means the model
   extracted the evidence right and only the verdict string was wrong.
2. Prompt contract: which task prompts actually enumerate the four legal
   verdicts. Each model call is isolated, so a task that says "same schema"
   never shows the model the label set.
3. Run-to-run instability: task-arms whose 3 trials produced 2+ distinct
   verdict strings at temperature 0.0.

This script never touches the grader, golds, reference/decoy answers, or
historical summaries. It imports the grader only to reuse field definitions.

Usage: .venv/bin/python reports/diagnostic_labels.py
Writes: reports/diagnostic-YYYYMMDD.json (regenerable, dated)
"""

from __future__ import annotations

import glob
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

VALID = ("CONFIRMED", "SUSPICIOUS", "NOT_FOUND", "UNVERIFIED")


def load_trials() -> list[dict]:
    """All trial records: legacy transcripts dir + completed Gemini run dir."""
    files = glob.glob(str(ROOT / "results" / "transcripts" / "*.json"))
    files += glob.glob(
        str(ROOT / "results" / "runs" / "gemini-gemini-2.5-flash-20261108T172302Z" / "*.json")
    )
    trials = [json.loads(Path(f).read_text(encoding="utf-8")) for f in files]
    deduped = {}
    for t in trials:
        deduped[(t.get("backend"), t["task_id"], t["run"])] = t
    return list(deduped.values())


def failure_split(trials: list[dict]) -> dict:
    """Split FAILED model trials; GPT excluded (aggregate-only, no transcripts)."""
    out: dict = {}
    for backend in ("muse", "openrouter", "gemini"):
        ds = [t for t in trials if t.get("backend") == backend]
        by_key = {(t["task_id"], t["run"]): t for t in ds}
        ds = list(by_key.values())
        fails = [t for t in ds if not t["grade"]["passed"]]
        pure = [
            t
            for t in fails
            if t["grade"]["fields_matched"] == t["grade"]["fields_total"]
        ]
        fallbacks = [t for t in fails if t.get("prediction", {}).get("parse_error")]
        field_err = [t for t in fails if t not in pure]
        out[backend] = {
            "trials": len(ds),
            "failed": len(fails),
            "pure_label_fail": len(pure),
            "field_error_fail": len(field_err),
            "parse_fallback": len(fallbacks),
            "false_confirmed": sum(
                1 for t in ds if t["grade"]["catastrophic_false_confirmed"]
            ),
        }
    return out


def prompt_contract() -> dict:
    """Which task prompts show the model the four legal verdicts?"""
    rows = {}
    for path in sorted((ROOT / "tasks").glob("T*.json")):
        task = json.loads(path.read_text(encoding="utf-8"))
        rows[task["id"]] = "CONFIRMED | SUSPICIOUS" in task["prompt"]
    return rows


def instability(trials: list[dict]) -> dict:
    """Task-arms with 2+ distinct verdict strings across trials (temp 0.0)."""
    by_arm: dict = defaultdict(set)
    for t in trials:
        if t.get("backend") not in ("muse", "openrouter", "gemini"):
            continue
        by_arm[(t["backend"], t["task_id"])].add(
            str(t.get("prediction", {}).get("verdict"))
        )
    unstable = {
        f"{be} {tid}": sorted(vs)
        for (be, tid), vs in by_arm.items()
        if len(vs) > 1
    }
    return {"unstable_arms": unstable, "n_unstable": len(unstable), "n_arms": len(by_arm)}


def main() -> None:
    trials = load_trials()
    split = failure_split(trials)
    contract = prompt_contract()
    stab = instability(trials)
    totals = {
        k: sum(v[k] for v in split.values())
        for k in ("trials", "failed", "pure_label_fail", "field_error_fail",
                  "parse_fallback", "false_confirmed")
    }
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": "Post-hoc diagnostic for disclosure. Not a rescore: "
        "grader, golds, reference/decoy answers and historical summaries "
        "are untouched.",
        "failure_split_per_arm": split,
        "failure_split_totals": totals,
        "prompt_contract_enumerates_verdicts": contract,
        "prompts_enumerating": sum(contract.values()),
        "n_prompts": len(contract),
        "instability": stab,
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = ROOT / "reports" / f"diagnostic-{stamp}.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("## Failure split (failed trials only; GPT aggregate-only, excluded)")
    for be, v in split.items():
        print(
            f"- {be}: {v['failed']} failed = {v['pure_label_fail']} pure-label "
            f"+ {v['field_error_fail']} field-error "
            f"(incl. {v['parse_fallback']} parse fallbacks), "
            f"false CONFIRMED {v['false_confirmed']}"
        )
    print(f"TOTAL: {totals['failed']} failed = {totals['pure_label_fail']} "
          f"pure-label + {totals['field_error_fail']} field-error")
    print(f"\n## Prompt contract: {sum(contract.values())}/{len(contract)} "
          "prompts enumerate the verdict set")
    print("Enumerates:", [k for k, v in contract.items() if v])
    print(f"\n## Instability: {stab['n_unstable']}/{stab['n_arms']} task-arms "
          "gave 2+ distinct verdicts at temp 0.0")
    print(f"Wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
