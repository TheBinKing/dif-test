"""Notification plugin — logs task events and optionally writes to a file."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from task_manager.events import Event, EventType, EventBus
from task_manager.plugins import BasePlugin, PluginMeta

logger = logging.getLogger(__name__)


class NotificationPlugin(BasePlugin):
    """Writes human-readable notifications for key task events.

    Config keys:
        log_file (str): Optional path to an append-only JSON-lines log.
        notify_events (list[str]): Event type values to notify on.
            Defaults to completed, cancelled, and overdue.
    """

    @property
    def meta(self) -> PluginMeta:
        return PluginMeta(
            name="notifications",
            version="1.0.0",
            description="Log and optionally persist task event notifications",
            author="TaskManager Team",
        )

    def activate(self) -> None:
        notify_events = self.config.get("notify_events", [
            EventType.TASK_COMPLETED.value,
            EventType.TASK_CANCELLED.value,
            EventType.TASK_OVERDUE.value,
            EventType.TASK_ASSIGNED.value,
        ])
        self._target_types = {EventType(v) for v in notify_events}
        self._log_path: Optional[Path] = None

        log_file = self.config.get("log_file")
        if log_file:
            self._log_path = Path(log_file)
            self._log_path.parent.mkdir(parents=True, exist_ok=True)

        # Subscribe to wildcard and filter inside handler
        self.bus.subscribe(None, self._handle)

    def deactivate(self) -> None:
        self.bus.unsubscribe(None, self._handle)

    def _handle(self, event: Event) -> None:
        if event.event_type not in self._target_types:
            return

        message = self._format(event)
        logger.info("NOTIFICATION: %s", message)

        if self._log_path:
            record = {
                "timestamp": event.timestamp.isoformat(),
                "type": event.event_type.value,
                "task_id": event.task_id,
                "message": message,
                "payload": {
                    k: (v.isoformat() if isinstance(v, datetime) else v)
                    for k, v in event.payload.items()
                },
            }
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    @staticmethod
    def _format(event: Event) -> str:
        title = event.payload.get("title", event.task_id or "unknown")
        messages = {
            EventType.TASK_COMPLETED: f"✅ Task completed: {title}",
            EventType.TASK_CANCELLED: f"🚫 Task cancelled: {title}",
            EventType.TASK_OVERDUE: f"⏰ Task overdue: {title}",
            EventType.TASK_ASSIGNED: (
                f"👤 Task assigned: {title} → "
                f"{event.payload.get('assignee', '?')}"
            ),
        }
        return messages.get(event.event_type, f"Event: {event.key}")
