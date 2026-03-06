"""Command-line interface for TaskManager."""

from __future__ import annotations

import argparse
import sys

from task_manager.models import Task, TaskStatus, Priority
from task_manager.storage import TaskStore

# Global store instance
_store = TaskStore()


def cmd_add(args: argparse.Namespace) -> None:
    """Handle the add command."""
    priority = Priority[args.priority.upper()]
    task = Task(
        title=args.title,
        description=args.description or "",
        priority=priority,
    )
    task_id = _store.add(task)
    print(f"Created task [{task_id}]: {task.title}")


def cmd_list(args: argparse.Namespace) -> None:
    """Handle the list command."""
    if args.status:
        status = TaskStatus(args.status)
        tasks = _store.filter_by_status(status)
    else:
        tasks = _store.list_all()

    if not tasks:
        print("No tasks found.")
        return

    for t in tasks:
        flag = "done" if t.status == TaskStatus.DONE else "open"
        print(f"  [{flag}] [{t.task_id}] {t.title}  (P:{t.priority.name}, {t.status.value})")


def cmd_done(args: argparse.Namespace) -> None:
    """Handle the done command."""
    task = _store.get(args.task_id)
    if task is None:
        print(f"Task {args.task_id} not found.")
        sys.exit(1)
    task.mark_done()
    print(f"Task [{args.task_id}] marked as done.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taskm", description="Simple Task Manager")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title")
    p_add.add_argument("-d", "--description", default="")
    p_add.add_argument("-p", "--priority", default="medium", choices=["low", "medium", "high"])

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("-s", "--status", choices=["todo", "in_progress", "done"])

    # done
    p_done = sub.add_parser("done", help="Mark a task as done")
    p_done.add_argument("task_id")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "add": cmd_add,
        "list": cmd_list,
        "done": cmd_done,
    }

    if args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
