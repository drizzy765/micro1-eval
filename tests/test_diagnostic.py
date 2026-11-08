"""Regression tests for the label diagnostic's evidence gate.

The diagnostic must refuse to write any output when required trial
evidence is absent or incomplete, so a partial tree can never produce a
plausibly complete-looking report.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reports.diagnostic_labels import (  # noqa: E402
    IncompleteEvidenceError,
    compute_report,
    load_trials,
    validate_trials,
)

TASK_IDS = [f"T{i:02d}" for i in range(1, 11)]


def _trial(backend: str, task_id: str, run: int) -> dict:
    return {
        "backend": backend,
        "task_id": task_id,
        "run": run,
        "prediction": {"verdict": "SUSPICIOUS"},
        "grade": {
            "passed": False,
            "fields_matched": 7,
            "fields_total": 7,
            "catastrophic_false_confirmed": False,
        },
    }


def _full_coverage() -> list[dict]:
    return [
        _trial(be, tid, run)
        for be in ("muse", "openrouter", "gemini")
        for tid in TASK_IDS
        for run in (1, 2, 3)
    ]


def test_full_coverage_passes_validation():
    validate_trials(_full_coverage(), TASK_IDS)


def test_missing_trial_raises_before_any_output():
    trials = [t for t in _full_coverage() if (t["backend"], t["task_id"], t["run"]) != ("gemini", "T10", 3)]
    with pytest.raises(IncompleteEvidenceError) as exc:
        validate_trials(trials, TASK_IDS)
    assert "gemini" in str(exc.value)


def test_empty_evidence_raises():
    with pytest.raises(IncompleteEvidenceError):
        validate_trials([], TASK_IDS)


def test_main_writes_nothing_when_evidence_missing(tmp_path: Path):
    from reports.diagnostic_labels import main

    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    shutil.copy(ROOT / "tasks" / "catalog.json", tasks_dir / "catalog.json")
    (tmp_path / "results").mkdir()
    with pytest.raises(IncompleteEvidenceError):
        main(root=tmp_path)
    assert list((tmp_path / "reports").glob("diagnostic-*.json")) == [] if (tmp_path / "reports").exists() else True


def test_live_counts_match_saved_audit():
    """Read-only: recomputed totals must equal the frozen diagnostic file."""
    trials = load_trials()
    report = compute_report(trials)
    saved = json.loads((ROOT / "reports" / "diagnostic-20261108.json").read_text(encoding="utf-8"))
    assert report["failure_split_totals"] == saved["failure_split_totals"]
    assert report["prompts_enumerating"] == saved["prompts_enumerating"]
    assert report["instability"]["n_unstable"] == saved["instability"]["n_unstable"]
