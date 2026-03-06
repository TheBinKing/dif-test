"""Command-line interface for TaskManager."""

from __future__ import annotations

import argparse
import sys

from task_manager.models import Task, TaskStatus, Priority
from task_manager.base_store import BaseTaskStore
from task_manager.json_store import JsonStore
from task_manager import stats as task_stats


def _get_store() -> BaseTaskStore:
    """Create the default storage backend."""
    return JsonStore("tasks.json")


def cmd_add(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Handle the add command."""
    priority = Priority[args.priority.upper()]
    task = Task(
        title=args.title,
        description=args.description or "",
        priority=priority,
    )
    if args.assignee:
        task.assign_to(args.assignee)
    task_id = store.add(task)
    print(f"Created task [{task_id}]: {task.title}")


def cmd_list(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Handle the list command."""
    if args.status:
        status = TaskStatus(args.status)
        tasks = store.filter_by_status(status)
    elif args.assignee:
        tasks = store.filter_by_assignee(args.assignee)
    else:
        tasks = store.list_all()

    if not tasks:
        print("No tasks found.")
        return

    for t in tasks:
        flag = "done" if t.status == TaskStatus.DONE else "open"
        overdue = " [OVERDUE]" if t.is_overdue else ""
        print(
            f"  [{flag}] [{t.task_id}] {t.title}"
            f"  (P:{t.priority.name}, {t.status.value}){overdue}"
        )


def cmd_done(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Handle the done command."""
    task = store.get(args.task_id)
    if task is None:
        print(f"Task {args.task_id} not found.")
        sys.exit(1)
    task.mark_done()
    store.update(task)
    print(f"Task [{args.task_id}] marked as done.")


def cmd_search(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Handle the search command."""
    results = store.search(args.keyword)
    if not results:
        print("No matching tasks.")
        return
    for t in results:
        print(f"  [{t.task_id}] {t.title}  ({t.status.value})")


def cmd_stats(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Handle the stats command."""
    s = task_stats.summary(store)
    print(task_stats.format_summary(s))


def cmd_remove(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Handle the remove command."""
    if store.remove(args.task_id):
        print(f"Task [{args.task_id}] removed.")
    else:
        print(f"Task {args.task_id} not found.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taskm", description="TaskManager CLI"
    )
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title")
    p_add.add_argument("-d", "--description", default="")
    p_add.add_argument(
        "-p", "--priority", default="medium",
        choices=["low", "medium", "high", "critical"],
    )
    p_add.add_argument("-a", "--assignee", default=None)

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument(
        "-s", "--status",
        choices=["todo", "in_progress", "done", "cancelled"],
    )
    p_list.add_argument("-a", "--assignee", default=None)

    # done
    p_done = sub.add_parser("done", help="Mark a task as done")
    p_done.add_argument("task_id")

    # search
    p_search = sub.add_parser("search", help="Search tasks by keyword")
    p_search.add_argument("keyword")

    # stats
    sub.add_parser("stats", help="Show task statistics")

    # remove
    p_rm = sub.add_parser("remove", help="Remove a task")
    p_rm.add_argument("task_id")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    store = _get_store()

    handlers = {
        "add": cmd_add,
        "list": cmd_list,
        "done": cmd_done,
        "search": cmd_search,
        "stats": cmd_stats,
        "remove": cmd_remove,
    }

    if args.command in handlers:
        handlers[args.command](store, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
