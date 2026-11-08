"""Post-hoc semantic-vs-format diagnostic (disclosure only, never a rescore).

Reads intact trial transcripts plus task prompts and reports three tables:

1. Failure split per arm: pure-label (all compared fields correct) vs
   field-error vs parse-fallback. A pure-label failure means the model
   extracted the evidence right and only the verdict string was wrong.
2. Prompt contract: which task prompts actually enumerate the four legal
   verdicts. Each model call is isolated, so a task that says "same schema"
   never shows the model the label set.
3. Raw-string variation: task-arms whose 3 trials produced 2+ distinct
   verdict strings at temperature 0.0. Case-only and synonym differences
   are reported as string variation, not as proven semantic instability.

Evidence gate: the script refuses to write any output unless every
expected (backend, task, run) trial is present. A partial tree fails
loudly instead of producing a plausibly complete-looking report.

This script never touches the grader, golds, reference/decoy answers, or
historical summaries.

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

EXPECTED_BACKENDS = ("muse", "openrouter", "gemini")
EXPECTED_RUNS = (1, 2, 3)


class IncompleteEvidenceError(Exception):
    """Raised before any output is written when trial evidence is missing."""


def transcript_dirs(root: Path) -> list[Path]:
    return [
        root / "results" / "transcripts",
        root / "results" / "runs" / "gemini-gemini-2.5-flash-20261108T172302Z",
    ]


def load_trials(dirs: list[Path] | None = None) -> list[dict]:
    """All trial records: legacy transcripts dir + completed Gemini run dir."""
    if dirs is None:
        dirs = transcript_dirs(ROOT)
    files: list[str] = []
    for d in dirs:
        files += glob.glob(str(d / "*.json"))
    trials = [json.loads(Path(f).read_text(encoding="utf-8")) for f in files]
    deduped = {}
    for t in trials:
        deduped[(t.get("backend"), t["task_id"], t["run"])] = t
    return list(deduped.values())


def expected_keys(task_ids: list[str]) -> set[tuple]:
    return {
        (be, tid, run)
        for be in EXPECTED_BACKENDS
        for tid in task_ids
        for run in EXPECTED_RUNS
    }


def validate_trials(trials: list[dict], task_ids: list[str]) -> dict:
    """Fail loudly on absent/incomplete evidence. Writes nothing; returns
    per-backend trial counts when everything expected is present."""
    present = {(t.get("backend"), t["task_id"], t["run"]) for t in trials}
    missing = sorted(expected_keys(task_ids) - present)
    if missing:
        by_backend: dict = {}
        for be, tid, run in missing:
            by_backend.setdefault(be, []).append(f"{tid} run{run}")
        detail = "; ".join(
            f"{be}: {len(v)} missing ({', '.join(v[:5])}{'...' if len(v) > 5 else ''})"
            for be, v in sorted(by_backend.items())
        )
        raise IncompleteEvidenceError(
            f"Incomplete trial evidence: {len(missing)} of "
            f"{len(expected_keys(task_ids))} expected (backend, task, run) "
            f"trials missing [{detail}]. Refusing to write a diagnostic. "
            "Restore results/transcripts/ and the completed Gemini run dir."
        )
    return {
        be: sum(1 for t in trials if t.get("backend") == be)
        for be in EXPECTED_BACKENDS
    }


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


def prompt_contract(root: Path = ROOT) -> dict:
    """Which task prompts show the model the four legal verdicts?"""
    rows = {}
    for path in sorted((root / "tasks").glob("T*.json")):
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


def task_ids(root: Path = ROOT) -> list[str]:
    catalog = json.loads((root / "tasks" / "catalog.json").read_text(encoding="utf-8"))
    return list(catalog["task_ids"])


def compute_report(trials: list[dict], root: Path = ROOT) -> dict:
    """Build the report dict from validated trials. Writes nothing."""
    split = failure_split(trials)
    contract = prompt_contract(root)
    stab = instability(trials)
    totals = {
        k: sum(v[k] for v in split.values())
        for k in ("trials", "failed", "pure_label_fail", "field_error_fail",
                  "parse_fallback", "false_confirmed")
    }
    return {
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


def main(root: Path = ROOT) -> None:
    trials = load_trials(transcript_dirs(root))
    validate_trials(trials, task_ids(root))
    report = compute_report(trials, root)
    split = report["failure_split_per_arm"]
    totals = report["failure_split_totals"]
    contract = report["prompt_contract_enumerates_verdicts"]
    stab = report["instability"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = root / "reports" / f"diagnostic-{stamp}.json"
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
    print(f"\n## Raw-string variation: {stab['n_unstable']}/{stab['n_arms']} "
          "task-arms gave 2+ distinct verdict strings at temp 0.0")
    print(f"Wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
