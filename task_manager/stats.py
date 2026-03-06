"""Task statistics and reporting."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from task_manager.base_store import BaseTaskStore

from task_manager.models import TaskStatus, Priority


def summary(store: BaseTaskStore) -> dict:
    """Generate a summary of all tasks."""
    tasks = store.list_all()
    status_counts = Counter(t.status for t in tasks)
    priority_counts = Counter(t.priority for t in tasks)
    overdue = [t for t in tasks if t.is_overdue]

    return {
        "total": len(tasks),
        "by_status": {s.value: status_counts.get(s, 0) for s in TaskStatus},
        "by_priority": {p.name: priority_counts.get(p, 0) for p in Priority},
        "overdue_count": len(overdue),
        "completion_rate": (
            status_counts.get(TaskStatus.DONE, 0) / len(tasks)
            if tasks else 0.0
        ),
    }


def format_summary(stats: dict) -> str:
    """Format statistics as a human-readable string."""
    lines = [
        f"Total tasks: {stats['total']}",
        "",
        "By status:",
    ]
    for status, count in stats["by_status"].items():
        lines.append(f"  {status}: {count}")

    lines.append("")
    lines.append("By priority:")
    for prio, count in stats["by_priority"].items():
        lines.append(f"  {prio}: {count}")

    lines.append("")
    lines.append(f"Overdue: {stats['overdue_count']}")
    lines.append(f"Completion rate: {stats['completion_rate']:.0%}")

    return "\n".join(lines)
