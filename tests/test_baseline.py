from pathlib import Path

from baseline.verdict import decide_verdict
from grader.grade import grade_prediction
from runner.io_utils import load_tasks

TASKS = load_tasks(Path(__file__).resolve().parents[1] / "tasks")


def test_baseline_passes_every_task():
    failures = []
    for task in TASKS:
        pred = decide_verdict(task)
        grade = grade_prediction(pred, task["gold"])
        if not grade.passed:
            failures.append({"task": task["id"], "pred": pred, "grade": grade.to_dict()})
    assert failures == []


def test_baseline_never_false_confirms():
    for task in TASKS:
        pred = decide_verdict(task)
        grade = grade_prediction(pred, task["gold"])
        assert grade.catastrophic_false_confirmed is False, task["id"]
