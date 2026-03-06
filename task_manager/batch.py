"""Batch operations — bulk import, export, and status transitions."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from task_manager.base_store import BaseTaskStore
from task_manager.events import Event, EventType, get_event_bus
from task_manager.models import Task, TaskStatus

logger = logging.getLogger(__name__)


class BatchOperations:
    """High-level helpers for operating on tasks in bulk.

    All mutations emit events so plugins can react accordingly.
    """

    def __init__(self, store: BaseTaskStore) -> None:
        self.store = store
        self.bus = get_event_bus()

    # ── Bulk import / export ─────────────────────────────────────

    def import_from_json(self, file_path: str) -> list[Task]:
        """Import tasks from a JSON file (list of task dicts).

        Existing tasks with the same ID are **skipped** to avoid
        duplicates.

        Returns:
            List of newly imported Task objects.
        """
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        imported: list[Task] = []
        skipped = 0
        for item in data:
            task = Task.from_dict(item)
            if self.store.get(task.task_id) is not None:
                skipped += 1
                continue
            self.store.add(task)
            imported.append(task)

        logger.info(
            "Imported %d tasks (%d skipped) from %s",
            len(imported),
            skipped,
            path,
        )

        self.bus.emit(Event(
            EventType.BATCH_IMPORT,
            payload={
                "count": len(imported),
                "skipped": skipped,
                "source": str(path),
            },
        ))

        return imported

    def export_to_json(
        self,
        file_path: str,
        status_filter: Optional[TaskStatus] = None,
    ) -> int:
        """Export tasks to a JSON file.

        Args:
            file_path: Destination path.
            status_filter: If given, only export tasks with this status.

        Returns:
            Number of tasks exported.
        """
        if status_filter:
            tasks = self.store.filter_by_status(status_filter)
        else:
            tasks = self.store.list_all()

        data = [t.to_dict() for t in tasks]
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        self.bus.emit(Event(
            EventType.BATCH_EXPORT,
            payload={
                "count": len(data),
                "destination": str(path),
                "tasks": tasks,
            },
        ))

        logger.info("Exported %d tasks to %s", len(data), path)
        return len(data)

    # ── Bulk status transitions ──────────────────────────────────

    def complete_all(
        self,
        task_ids: Optional[list[str]] = None,
    ) -> int:
        """Mark multiple tasks as done.

        Args:
            task_ids: Specific IDs, or *None* to complete **all** open
                tasks.

        Returns:
            Number of tasks transitioned.
        """
        if task_ids is None:
            tasks = [
                t for t in self.store.list_all()
                if t.status not in (TaskStatus.DONE, TaskStatus.CANCELLED)
            ]
        else:
            tasks = [
                self.store.get(tid) for tid in task_ids
                if self.store.get(tid) is not None
            ]

        count = 0
        for task in tasks:
            if task.status != TaskStatus.DONE:
                task.mark_done()
                self.store.update(task)
                self.bus.emit(Event(
                    EventType.TASK_COMPLETED,
                    task_id=task.task_id,
                    payload={"title": task.title},
                ))
                count += 1

        logger.info("Batch completed %d tasks", count)
        return count

    def cancel_all(
        self,
        task_ids: Optional[list[str]] = None,
    ) -> int:
        """Cancel multiple tasks.

        Args:
            task_ids: Specific IDs, or *None* to cancel **all**
                non-done tasks.

        Returns:
            Number of tasks cancelled.
        """
        if task_ids is None:
            tasks = [
                t for t in self.store.list_all()
                if t.status not in (TaskStatus.DONE, TaskStatus.CANCELLED)
            ]
        else:
            tasks = [
                self.store.get(tid) for tid in task_ids
                if self.store.get(tid) is not None
            ]

        count = 0
        for task in tasks:
            if task.status != TaskStatus.CANCELLED:
                task.cancel()
                self.store.update(task)
                self.bus.emit(Event(
                    EventType.TASK_CANCELLED,
                    task_id=task.task_id,
                    payload={"title": task.title},
                ))
                count += 1

        logger.info("Batch cancelled %d tasks", count)
        return count

    def reassign_all(
        self,
        task_ids: list[str],
        new_assignee: str,
    ) -> int:
        """Re-assign a batch of tasks to a new user.

        Returns:
            Number of tasks re-assigned.
        """
        count = 0
        for tid in task_ids:
            task = self.store.get(tid)
            if task is not None:
                old = task.assignee
                task.assign_to(new_assignee)
                self.store.update(task)
                self.bus.emit(Event(
                    EventType.TASK_ASSIGNED,
                    task_id=task.task_id,
                    payload={
                        "title": task.title,
                        "assignee": new_assignee,
                        "previous_assignee": old,
                    },
                ))
                count += 1

        logger.info(
            "Batch reassigned %d tasks → %s", count, new_assignee,
        )
        return count

    # ── Duplicate detection ──────────────────────────────────────

    def find_duplicates(self, threshold: float = 0.8) -> list[tuple[Task, Task]]:
        """Find tasks with suspiciously similar titles.

        Uses a simple Jaccard similarity on title word sets.

        Args:
            threshold: Similarity ratio (0.0 – 1.0) above which
                two tasks are considered potential duplicates.

        Returns:
            List of (task_a, task_b) pairs.
        """
        tasks = self.store.list_all()
        duplicates: list[tuple[Task, Task]] = []
        seen: set[tuple[str, str]] = set()

        for i, a in enumerate(tasks):
            words_a = set(a.title.lower().split())
            for b in tasks[i + 1:]:
                key = tuple(sorted([a.task_id, b.task_id]))
                if key in seen:
                    continue
                seen.add(key)

                words_b = set(b.title.lower().split())
                if not words_a or not words_b:
                    continue

                intersection = words_a & words_b
                union = words_a | words_b
                similarity = len(intersection) / len(union)

                if similarity >= threshold:
                    duplicates.append((a, b))

        return duplicates
