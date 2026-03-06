"""JSON file-based persistent storage backend."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from task_manager.models import Task, TaskStatus
from task_manager.base_store import BaseTaskStore


class JsonStore(BaseTaskStore):
    """Persistent storage using a local JSON file."""

    def __init__(self, file_path: str = "tasks.json") -> None:
        self._path = Path(file_path)
        self._tasks: dict[str, Task] = {}
        self._load()

    def _load(self) -> None:
        """Load tasks from JSON file."""
        if self._path.exists():
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._tasks = {
                item["task_id"]: Task.from_dict(item)
                for item in data
            }

    def _save(self) -> None:
        """Persist tasks to JSON file."""
        data = [t.to_dict() for t in self._tasks.values()]
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, task: Task) -> str:
        self._tasks[task.task_id] = task
        self._save()
        return task.task_id

    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def update(self, task: Task) -> None:
        if task.task_id in self._tasks:
            self._tasks[task.task_id] = task
            self._save()

    def remove(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save()
            return True
        return False

    def list_all(self) -> list[Task]:
        return sorted(
            self._tasks.values(),
            key=lambda t: t.priority.value,
            reverse=True,
        )

    def filter_by_status(self, status: TaskStatus) -> list[Task]:
        return [t for t in self._tasks.values() if t.status == status]

    def filter_by_assignee(self, assignee: str) -> list[Task]:
        return [t for t in self._tasks.values() if t.assignee == assignee]

    def search(self, keyword: str) -> list[Task]:
        kw = keyword.lower()
        return [
            t for t in self._tasks.values()
            if kw in t.title.lower() or kw in t.description.lower()
        ]

    @property
    def count(self) -> int:
        return len(self._tasks)
