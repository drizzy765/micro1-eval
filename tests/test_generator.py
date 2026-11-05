from pathlib import Path

from generator.receipts import DISCLAIMER, generate_receipt
from PIL import Image
from runner.io_utils import load_tasks

ROOT = Path(__file__).resolve().parents[1]


def test_generator_writes_at_least_two_receipts(tmp_path):
    tasks = load_tasks(ROOT / "tasks")
    written = []
    for task in tasks[:2]:
        dest = tmp_path / f"{task['id']}.png"
        generate_receipt(task["image_spec"], dest)
        assert dest.exists() and dest.stat().st_size > 1000
        img = Image.open(dest)
        assert img.size[0] == 720
        written.append(dest)
    assert len(written) == 2


def test_disclaimer_is_defined_and_mentions_fictional():
    assert "FICTIONAL RECEIPT" in DISCLAIMER
    assert "No real logos" in DISCLAIMER
