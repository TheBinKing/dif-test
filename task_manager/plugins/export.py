"""Export plugin — provides CSV, JSON, and Markdown export capabilities."""

from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from task_manager.events import Event, EventType
from task_manager.plugins import BasePlugin, PluginMeta
from task_manager.base_store import BaseTaskStore
from task_manager.models import Task

logger = logging.getLogger(__name__)


class ExportFormat:
    """Supported export output formats."""

    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"


class ExportPlugin(BasePlugin):
    """Export tasks to various file formats.

    Listens for ``BATCH_EXPORT`` events or can be invoked directly
    via the ``export_tasks`` method.

    Config keys:
        default_format (str): One of json / csv / markdown.
        output_dir (str): Default directory to write exports.
    """

    @property
    def meta(self) -> PluginMeta:
        return PluginMeta(
            name="export",
            version="1.0.0",
            description="Export tasks to JSON, CSV, and Markdown formats",
            author="TaskManager Team",
        )

    def activate(self) -> None:
        self._default_format = self.config.get("default_format", ExportFormat.JSON)
        self._output_dir = Path(self.config.get("output_dir", "."))
        self.bus.subscribe(EventType.BATCH_EXPORT, self._handle_export)

    def deactivate(self) -> None:
        self.bus.unsubscribe(EventType.BATCH_EXPORT, self._handle_export)

    def _handle_export(self, event: Event) -> None:
        """Handle export events from the event bus."""
        tasks = event.payload.get("tasks", [])
        fmt = event.payload.get("format", self._default_format)
        output_path = event.payload.get("output_path")

        if tasks:
            self.export_tasks(tasks, fmt=fmt, output_path=output_path)

    # ── Public API ───────────────────────────────────────────────

    def export_tasks(
        self,
        tasks: list[Task],
        fmt: str = ExportFormat.JSON,
        output_path: Optional[str] = None,
    ) -> str:
        """Export a list of tasks to the specified format.

        Args:
            tasks: Tasks to export.
            fmt: Output format (json / csv / markdown).
            output_path: Optional file path; if None, returns
                the formatted string without writing.

        Returns:
            The formatted output as a string.
        """
        exporters = {
            ExportFormat.JSON: self._to_json,
            ExportFormat.CSV: self._to_csv,
            ExportFormat.MARKDOWN: self._to_markdown,
        }
        exporter = exporters.get(fmt)
        if exporter is None:
            raise ValueError(f"Unsupported export format: {fmt}")

        content = exporter(tasks)

        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            logger.info("Exported %d tasks to %s (%s)", len(tasks), path, fmt)

        return content

    # ── Format implementations ───────────────────────────────────

    @staticmethod
    def _to_json(tasks: list[Task]) -> str:
        data = [t.to_dict() for t in tasks]
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)

    @staticmethod
    def _to_csv(tasks: list[Task]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "task_id", "title", "description", "status",
            "priority", "assignee", "due_date", "created_at",
            "tags", "subtask_count", "progress",
        ])
        for t in tasks:
            writer.writerow([
                t.task_id,
                t.title,
                t.description,
                t.status.value,
                t.priority.name,
                t.assignee or "",
                t.due_date.isoformat() if t.due_date else "",
                t.created_at.isoformat(),
                ";".join(t.tags),
                len(t.subtasks),
                f"{t.progress:.0%}",
            ])
        return output.getvalue()

    @staticmethod
    def _to_markdown(tasks: list[Task]) -> str:
        lines = ["# Task Export", ""]
        lines.append(
            "| ID | Title | Status | Priority | Assignee | Progress |"
        )
        lines.append(
            "|---|---|---|---|---|---|"
        )
        for t in tasks:
            lines.append(
                f"| {t.task_id} | {t.title} | {t.status.value} "
                f"| {t.priority.name} | {t.assignee or '-'} "
                f"| {t.progress:.0%} |"
            )
        lines.append("")
        lines.append(f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        return "\n".join(lines)
