"""Task data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class TaskStatus(Enum):
    """Possible states of a task."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    """Represents a single task in the system."""
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    assignee: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    task_id: str = field(default_factory=lambda: uuid4().hex[:8])

    def mark_done(self) -> None:
        """Mark the task as completed."""
        self.status = TaskStatus.DONE
        self.updated_at = datetime.now()

    def start(self) -> None:
        """Move task to in-progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def assign_to(self, user: str) -> None:
        """Assign this task to a user."""
        self.assignee = user
        self.updated_at = datetime.now()
