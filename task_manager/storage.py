"""In-memory storage backend for tasks."""

from __future__ import annotations

from typing import Optional

from task_manager.models import Task, TaskStatus


class TaskStore:
    """Simple in-memory task storage."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def add(self, task: Task) -> str:
        """Add a task and return its ID."""
        self._tasks[task.task_id] = task
        return task.task_id

    def get(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        return self._tasks.get(task_id)

    def remove(self, task_id: str) -> bool:
        """Remove a task. Returns True if it existed."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def list_all(self) -> list[Task]:
        """Return all tasks ordered by priority (high first)."""
        return sorted(
            self._tasks.values(),
            key=lambda t: t.priority.value,
            reverse=True,
        )

    def filter_by_status(self, status: TaskStatus) -> list[Task]:
        """Return tasks matching a given status."""
        return [t for t in self._tasks.values() if t.status == status]

    def filter_by_assignee(self, assignee: str) -> list[Task]:
        """Return tasks assigned to a specific user."""
        return [t for t in self._tasks.values() if t.assignee == assignee]

    @property
    def count(self) -> int:
        """Total number of tasks."""
        return len(self._tasks)
