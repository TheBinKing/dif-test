"""Event system for task lifecycle hooks.

Implements an observable pattern allowing components to subscribe
to and react to task state changes via a centralized event bus.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events emitted by the task system."""

    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_CANCELLED = "task_cancelled"
    TASK_DELETED = "task_deleted"
    TASK_ASSIGNED = "task_assigned"
    TASK_OVERDUE = "task_overdue"
    SUBTASK_ADDED = "subtask_added"
    SUBTASK_COMPLETED = "subtask_completed"
    BATCH_IMPORT = "batch_import"
    BATCH_EXPORT = "batch_export"


@dataclass
class Event:
    """An event carrying data about a task system change."""

    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    task_id: Optional[str] = None
    payload: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        """Short string identifier for logging."""
        return f"{self.event_type.value}:{self.task_id or 'system'}"


# Type alias for event handler callbacks
EventHandler = Callable[[Event], None]


class EventBus:
    """Central event dispatcher.

    Supports subscribing handlers to specific event types or
    a wildcard (*) that receives all events.  Handlers are invoked
    synchronously in registration order.

    Example::

        bus = EventBus()

        def on_task_done(event: Event):
            print(f"Task {event.task_id} completed!")

        bus.subscribe(EventType.TASK_COMPLETED, on_task_done)
        bus.emit(Event(EventType.TASK_COMPLETED, task_id="abc123"))
    """

    def __init__(self) -> None:
        self._handlers: dict[Optional[EventType], list[EventHandler]] = {}
        self._history: list[Event] = []
        self._max_history = 1000

    def subscribe(
        self,
        event_type: Optional[EventType],
        handler: EventHandler,
    ) -> None:
        """Register a handler for a specific event type.

        Pass ``None`` as *event_type* to subscribe to **all** events.
        """
        self._handlers.setdefault(event_type, []).append(handler)
        logger.debug(
            "Subscribed %s to %s",
            handler.__name__,
            event_type.value if event_type else "*",
        )

    def unsubscribe(
        self,
        event_type: Optional[EventType],
        handler: EventHandler,
    ) -> None:
        """Remove a previously registered handler."""
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event: Event) -> None:
        """Dispatch an event to all matching handlers."""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Type-specific handlers
        for handler in self._handlers.get(event.event_type, []):
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Handler %s failed for %s", handler.__name__, event.key,
                )

        # Wildcard handlers
        for handler in self._handlers.get(None, []):
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Wildcard handler %s failed for %s",
                    handler.__name__,
                    event.key,
                )

    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 50,
    ) -> list[Event]:
        """Retrieve recent events, optionally filtered by type."""
        if event_type is None:
            return self._history[-limit:]
        return [e for e in self._history if e.event_type == event_type][-limit:]

    def clear_history(self) -> None:
        """Wipe the event log."""
        self._history.clear()

    @property
    def handler_count(self) -> int:
        """Total number of registered handlers."""
        return sum(len(h) for h in self._handlers.values())


# Module-level singleton so all components share one bus.
_default_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Return the global EventBus singleton."""
    global _default_bus
    if _default_bus is None:
        _default_bus = EventBus()
    return _default_bus


def reset_event_bus() -> None:
    """Reset the global bus (useful in tests)."""
    global _default_bus
    _default_bus = None
