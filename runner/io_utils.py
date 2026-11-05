from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_tasks(tasks_dir: Path | None = None) -> list[dict[str, Any]]:
    tasks_dir = tasks_dir or (repo_root() / "tasks")
    catalog = load_json(tasks_dir / "catalog.json")
    tasks = []
    for task_id in catalog["task_ids"]:
        tasks.append(load_json(tasks_dir / f"{task_id}.json"))
    return tasks


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_manifest(paths: list[Path]) -> dict[str, str]:
    return {str(path.as_posix()): sha256_file(path) for path in paths}
