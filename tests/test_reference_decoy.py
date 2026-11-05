from pathlib import Path

from grader.grade import grade_prediction
from runner.io_utils import load_tasks

TASKS = load_tasks(Path(__file__).resolve().parents[1] / "tasks")


def test_catalog_has_eight_to_ten_tasks():
    assert 8 <= len(TASKS) <= 10


def test_every_reference_answer_passes_and_every_decoy_fails():
    failures = []
    for task in TASKS:
        ref = grade_prediction(task["reference_answer"], task["gold"])
        decoy = grade_prediction(task["decoy_answer"], task["gold"])
        if not ref.passed:
            failures.append(f"{task['id']} reference failed: {ref.to_dict()}")
        if decoy.passed:
            failures.append(f"{task['id']} decoy unexpectedly passed: {decoy.to_dict()}")
    assert failures == []


def test_fake_receipts_have_a_false_confirmed_decoy():
    """Tasks whose gold is not CONFIRMED must include a catastrophic decoy."""
    checked = 0
    for task in TASKS:
        if task["gold"]["verdict"] == "CONFIRMED":
            continue
        decoy = grade_prediction(task["decoy_answer"], task["gold"])
        assert decoy.catastrophic_false_confirmed, task["id"]
        checked += 1
    assert checked >= 6
