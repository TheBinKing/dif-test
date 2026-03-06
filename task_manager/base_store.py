"""Abstract storage interface for tasks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from task_manager.models import Task, TaskStatus


class BaseTaskStore(ABC):
    """Abstract base class for task storage backends."""

    @abstractmethod
    def add(self, task: Task) -> str:
        """Add a task and return its ID."""

    @abstractmethod
    def get(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""

    @abstractmethod
    def update(self, task: Task) -> None:
        """Persist changes to an existing task."""

    @abstractmethod
    def remove(self, task_id: str) -> bool:
        """Remove a task. Returns True if it existed."""

    @abstractmethod
    def list_all(self) -> list[Task]:
        """Return all tasks ordered by priority (high first)."""

    @abstractmethod
    def filter_by_status(self, status: TaskStatus) -> list[Task]:
        """Return tasks matching a given status."""

    @abstractmethod
    def filter_by_assignee(self, assignee: str) -> list[Task]:
        """Return tasks assigned to a specific user."""

    @abstractmethod
    def search(self, keyword: str) -> list[Task]:
        """Search tasks by keyword in title and description."""

    @property
    @abstractmethod
    def count(self) -> int:
        """Total number of tasks."""
