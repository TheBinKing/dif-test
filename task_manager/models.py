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
    CANCELLED = "cancelled"


class Priority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SubTask:
    """A lightweight sub-task belonging to a parent task."""
    title: str
    done: bool = False
    subtask_id: str = field(default_factory=lambda: uuid4().hex[:6])

    def complete(self) -> None:
        self.done = True


@dataclass
class Task:
    """Represents a single task in the system."""
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    assignee: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    subtasks: list[SubTask] = field(default_factory=list)
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    task_id: str = field(default_factory=lambda: uuid4().hex[:8])

    def mark_done(self) -> None:
        """Mark the task as completed."""
        self.status = TaskStatus.DONE
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.now()

    def start(self) -> None:
        """Move task to in-progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def assign_to(self, user: str) -> None:
        """Assign this task to a user."""
        self.assignee = user
        self.updated_at = datetime.now()

    def add_subtask(self, title: str) -> SubTask:
        """Add a subtask and return it."""
        st = SubTask(title=title)
        self.subtasks.append(st)
        self.updated_at = datetime.now()
        return st

    @property
    def progress(self) -> float:
        """Return completion progress (0.0 to 1.0) based on subtasks."""
        if not self.subtasks:
            return 1.0 if self.status == TaskStatus.DONE else 0.0
        done = sum(1 for s in self.subtasks if s.done)
        return done / len(self.subtasks)

    @property
    def is_overdue(self) -> bool:
        """Check if the task has passed its due date."""
        if self.due_date is None:
            return False
        return datetime.now() > self.due_date and self.status != TaskStatus.DONE

    def to_dict(self) -> dict:
        """Serialize task to a dictionary."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assignee": self.assignee,
            "tags": self.tags,
            "subtasks": [
                {"subtask_id": s.subtask_id, "title": s.title, "done": s.done}
                for s in self.subtasks
            ],
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Deserialize a task from a dictionary."""
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data["status"]),
            priority=Priority(data["priority"]),
            assignee=data.get("assignee"),
            tags=data.get("tags", []),
            task_id=data["task_id"],
        )
        if data.get("due_date"):
            task.due_date = datetime.fromisoformat(data["due_date"])
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.updated_at = datetime.fromisoformat(data["updated_at"])
        task.subtasks = [
            SubTask(
                title=s["title"],
                done=s["done"],
                subtask_id=s["subtask_id"],
            )
            for s in data.get("subtasks", [])
        ]
        return task
