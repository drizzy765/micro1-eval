"""Render every task receipt into assets/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generator.receipts import write_task_receipts
from runner.io_utils import load_tasks


def main() -> None:
    tasks = load_tasks(ROOT / "tasks")
    written = write_task_receipts(tasks, ROOT / "assets")
    print(f"wrote {len(written)} receipts to {ROOT / 'assets'}")


if __name__ == "__main__":
    main()
