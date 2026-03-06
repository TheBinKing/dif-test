"""Command-line interface for TaskManager.

Provides commands for task management, batch operations, template-based
task creation, event history, import/export, duplicate detection, and
plugin management.
"""

from __future__ import annotations

import argparse
import json
import sys

from task_manager.models import Task, TaskStatus, Priority
from task_manager.base_store import BaseTaskStore
from task_manager.json_store import JsonStore
from task_manager.events import get_event_bus, Event, EventType
from task_manager import stats as task_stats


def _get_store() -> BaseTaskStore:
    """Create the default storage backend."""
    return JsonStore("tasks.json")


# ── Original commands ────────────────────────────────────────────

def cmd_add(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Handle the add command."""
    priority = Priority[args.priority.upper()]
    task = Task(
        title=args.title,
        description=args.description or "",
        priority=priority,
        tags=args.tags.split(",") if args.tags else [],
    )
    if args.assignee:
        task.assign_to(args.assignee)
    task_id = store.add(task)

    bus = get_event_bus()
    bus.emit(Event(
        EventType.TASK_CREATED,
        task_id=task_id,
        payload={"title": task.title, "priority": priority.name},
    ))

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
        tags = f" [{', '.join(t.tags)}]" if t.tags else ""
        progress = f" {t.progress:.0%}" if t.subtasks else ""
        print(
            f"  [{flag}] [{t.task_id}] {t.title}"
            f"  (P:{t.priority.name}, {t.status.value})"
            f"{tags}{progress}{overdue}"
        )


def cmd_done(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Handle the done command."""
    task = store.get(args.task_id)
    if task is None:
        print(f"Task {args.task_id} not found.")
        sys.exit(1)
    task.mark_done()
    store.update(task)

    bus = get_event_bus()
    bus.emit(Event(
        EventType.TASK_COMPLETED,
        task_id=task.task_id,
        payload={"title": task.title},
    ))

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
    bus = get_event_bus()
    task = store.get(args.task_id)
    if store.remove(args.task_id):
        bus.emit(Event(
            EventType.TASK_DELETED,
            task_id=args.task_id,
            payload={"title": task.title if task else "?"},
        ))
        print(f"Task [{args.task_id}] removed.")
    else:
        print(f"Task {args.task_id} not found.")


# ── New commands: templates ──────────────────────────────────────

def cmd_template_list(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """List available task templates."""
    from task_manager.templates import TemplateRegistry

    registry = TemplateRegistry("templates.json")

    builtins = TemplateRegistry.builtin_templates()
    custom = registry.list_all()

    print("Built-in templates:")
    for t in builtins:
        print(f"  [{t.name}] {t.title_pattern}  (P:{t.default_priority.name})")
        if t.subtask_titles:
            print(f"         Subtasks: {len(t.subtask_titles)}")

    if custom:
        print("\nCustom templates:")
        for t in custom:
            print(f"  [{t.name}] {t.title_pattern}")


def cmd_template_use(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Create a task from a template."""
    from task_manager.templates import TemplateRegistry

    registry = TemplateRegistry("templates.json")

    template = registry.get(args.template_name)
    if template is None:
        for bt in TemplateRegistry.builtin_templates():
            if bt.name == args.template_name:
                template = bt
                break

    if template is None:
        print(f"Template '{args.template_name}' not found.")
        sys.exit(1)

    overrides: dict[str, str] = {}
    if args.vars:
        for pair in args.vars:
            key, _, value = pair.partition("=")
            overrides[key.strip()] = value.strip()

    task = template.render(overrides)
    if args.assignee:
        task.assign_to(args.assignee)

    task_id = store.add(task)
    print(f"Created task [{task_id}] from template '{template.name}': {task.title}")
    if task.subtasks:
        print(f"  ({len(task.subtasks)} subtasks created)")


# ── New commands: batch operations ───────────────────────────────

def cmd_batch_complete(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Complete tasks in batch."""
    from task_manager.batch import BatchOperations

    batch = BatchOperations(store)
    ids = args.task_ids if args.task_ids else None
    count = batch.complete_all(ids)
    print(f"Completed {count} task(s).")


def cmd_batch_cancel(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Cancel tasks in batch."""
    from task_manager.batch import BatchOperations

    batch = BatchOperations(store)
    ids = args.task_ids if args.task_ids else None
    count = batch.cancel_all(ids)
    print(f"Cancelled {count} task(s).")


def cmd_import(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Import tasks from a JSON file."""
    from task_manager.batch import BatchOperations

    batch = BatchOperations(store)
    imported = batch.import_from_json(args.file)
    print(f"Imported {len(imported)} task(s) from {args.file}")


def cmd_export(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Export tasks to a file."""
    from task_manager.plugins.export import ExportPlugin

    tasks = store.list_all()
    plugin = ExportPlugin()
    content = plugin.export_tasks(
        tasks,
        fmt=args.format,
        output_path=args.output,
    )
    if not args.output:
        print(content)
    else:
        print(f"Exported {len(tasks)} task(s) to {args.output}")


def cmd_duplicates(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Find duplicate tasks."""
    from task_manager.batch import BatchOperations

    batch = BatchOperations(store)
    dupes = batch.find_duplicates(threshold=args.threshold)
    if not dupes:
        print("No duplicate tasks found.")
        return

    print(f"Found {len(dupes)} potential duplicate pair(s):")
    for a, b in dupes:
        print(f"  [{a.task_id}] {a.title}")
        print(f"  [{b.task_id}] {b.title}")
        print()


def cmd_history(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """Show recent event history."""
    bus = get_event_bus()
    events = bus.get_history(limit=args.limit)
    if not events:
        print("No events recorded in this session.")
        return

    for e in events:
        ts = e.timestamp.strftime("%H:%M:%S")
        print(f"  [{ts}] {e.event_type.value}: {e.payload.get('title', e.task_id or '-')}")


# ── New commands: plugins ────────────────────────────────────────

def cmd_plugins(store: BaseTaskStore, args: argparse.Namespace) -> None:
    """List loaded plugins."""
    from task_manager.plugins import PluginRegistry

    registry = PluginRegistry()
    loaded = registry.loaded
    if not loaded:
        print("No plugins loaded. Available plugins:")
        print("  - notifications: Task event notifications")
        print("  - export: Export tasks to JSON/CSV/Markdown")
        return

    print("Loaded plugins:")
    for name in loaded:
        plugin = registry.get(name)
        if plugin:
            m = plugin.meta
            print(f"  [{m.name}] v{m.version} — {m.description}")


# ── Parser builder ───────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="taskm", description="TaskManager CLI — v0.3.0"
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
    p_add.add_argument("-t", "--tags", default=None, help="Comma-separated tags")

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

    # ── template commands ────────────────────────────────────────
    p_tpl = sub.add_parser("template", help="Manage task templates")
    tpl_sub = p_tpl.add_subparsers(dest="template_cmd")

    tpl_sub.add_parser("list", help="List available templates")

    p_tpl_use = tpl_sub.add_parser("use", help="Create task from template")
    p_tpl_use.add_argument("template_name")
    p_tpl_use.add_argument(
        "-v", "--vars", nargs="*",
        help="Variable overrides: key=value",
    )
    p_tpl_use.add_argument("-a", "--assignee", default=None)

    # ── batch commands ───────────────────────────────────────────
    p_batch = sub.add_parser("batch", help="Batch operations")
    batch_sub = p_batch.add_subparsers(dest="batch_cmd")

    p_bc = batch_sub.add_parser("complete", help="Complete tasks in batch")
    p_bc.add_argument("task_ids", nargs="*", help="Task IDs (empty = all)")

    p_bx = batch_sub.add_parser("cancel", help="Cancel tasks in batch")
    p_bx.add_argument("task_ids", nargs="*", help="Task IDs (empty = all)")

    # ── import / export ──────────────────────────────────────────
    p_imp = sub.add_parser("import", help="Import tasks from JSON")
    p_imp.add_argument("file", help="Path to JSON file")

    p_exp = sub.add_parser("export", help="Export tasks")
    p_exp.add_argument(
        "-f", "--format", default="json",
        choices=["json", "csv", "markdown"],
    )
    p_exp.add_argument("-o", "--output", default=None, help="Output file path")

    # ── duplicates ───────────────────────────────────────────────
    p_dup = sub.add_parser("duplicates", help="Find duplicate tasks")
    p_dup.add_argument(
        "--threshold", type=float, default=0.8,
        help="Similarity threshold (0.0-1.0)",
    )

    # ── history ──────────────────────────────────────────────────
    p_hist = sub.add_parser("history", help="Show recent event history")
    p_hist.add_argument("-n", "--limit", type=int, default=20)

    # ── plugins ──────────────────────────────────────────────────
    sub.add_parser("plugins", help="List loaded plugins")

    return parser


def main() -> None:
    """Entry point for the CLI."""
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
        "import": cmd_import,
        "export": cmd_export,
        "duplicates": cmd_duplicates,
        "history": cmd_history,
        "plugins": cmd_plugins,
    }

    if args.command in handlers:
        handlers[args.command](store, args)
    elif args.command == "template":
        if args.template_cmd == "list":
            cmd_template_list(store, args)
        elif args.template_cmd == "use":
            cmd_template_use(store, args)
        else:
            parser.parse_args(["template", "--help"])
    elif args.command == "batch":
        if args.batch_cmd == "complete":
            cmd_batch_complete(store, args)
        elif args.batch_cmd == "cancel":
            cmd_batch_cancel(store, args)
        else:
            parser.parse_args(["batch", "--help"])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
