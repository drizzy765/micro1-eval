"""Run-directory provenance: every eval run lands in a unique directory and
never overwrites an existing run's transcripts."""

import json
import shutil
from pathlib import Path

import pytest

import runner.run as run_mod
from runner.io_utils import load_tasks
from runner.run import run_eval


@pytest.fixture()
def isolated_root(tmp_path, monkeypatch):
    root = tmp_path / "evalroot"
    shutil.copytree(Path(run_mod.__file__).resolve().parents[1] / "tasks", root / "tasks")
    (root / "results").mkdir()
    monkeypatch.setattr(run_mod, "repo_root", lambda: root)
    return root


def _fixed_stamp(monkeypatch, stamp="20261106T120000Z"):
    monkeypatch.setattr(run_mod, "_utc_stamp", lambda: stamp)


def test_run_writes_transcripts_to_unique_run_dir(isolated_root):
    summary = run_eval("baseline", "sellsafe_deterministic_baseline", 1)
    run_dir = isolated_root / summary["run_dir"]
    assert summary["run_id"] in run_dir.name
    assert run_dir.is_dir()
    assert len(list(run_dir.glob("*.json"))) == 10


def test_existing_run_dir_is_never_overwritten(isolated_root, monkeypatch):
    _fixed_stamp(monkeypatch)
    first = run_eval("baseline", "sellsafe_deterministic_baseline", 1)
    first_dir = isolated_root / first["run_dir"]
    before = {p.name: p.read_bytes() for p in sorted(first_dir.glob("*.json"))}
    assert len(before) == 10

    second = run_eval("baseline", "sellsafe_deterministic_baseline", 1)
    assert second["run_dir"] != first["run_dir"]

    after = {p.name: p.read_bytes() for p in sorted(first_dir.glob("*.json"))}
    assert after == before
    assert len(list((isolated_root / second["run_dir"]).glob("*.json"))) == 10


def test_summary_records_run_location(isolated_root):
    summary = run_eval("baseline", "sellsafe_deterministic_baseline", 1)
    assert (isolated_root / summary["run_dir"]).is_dir()
    assert summary["run_id"] in summary["run_dir"]
    record = json.loads((isolated_root / "results" / "latest_summary.json").read_text())
    assert record["run_dir"] == summary["run_dir"]
