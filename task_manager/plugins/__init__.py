"""Plugin architecture for TaskManager.

Provides a base class and registry for plugins that extend the system's
functionality.  Plugins register event handlers on load and can expose
custom CLI sub-commands.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from task_manager.events import EventBus, get_event_bus

logger = logging.getLogger(__name__)


@dataclass
class PluginMeta:
    """Metadata describing a plugin."""

    name: str
    version: str
    description: str
    author: str = ""


class BasePlugin(ABC):
    """Abstract base class for all TaskManager plugins.

    Lifecycle:
        1. ``__init__`` — receive the event bus and config dict
        2. ``activate()`` — called once during system startup
        3. (runtime — event handlers fire)
        4. ``deactivate()`` — called on shutdown or unload
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.bus = event_bus or get_event_bus()
        self.config = config or {}

    @property
    @abstractmethod
    def meta(self) -> PluginMeta:
        """Return metadata about this plugin."""

    @abstractmethod
    def activate(self) -> None:
        """Register event handlers and perform setup."""

    def deactivate(self) -> None:
        """Clean-up; default is a no-op."""

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Plugin {self.meta.name} v{self.meta.version}>"


class PluginRegistry:
    """Manages plugin discovery, loading, and lifecycle."""

    def __init__(self, event_bus: Optional[EventBus] = None) -> None:
        self.bus = event_bus or get_event_bus()
        self._plugins: dict[str, BasePlugin] = {}

    def register(
        self,
        plugin_cls: type[BasePlugin],
        config: Optional[dict[str, Any]] = None,
    ) -> BasePlugin:
        """Instantiate, activate, and register a plugin.

        Raises:
            ValueError: If a plugin with the same name is already loaded.
        """
        instance = plugin_cls(event_bus=self.bus, config=config)
        name = instance.meta.name

        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' is already registered")

        instance.activate()
        self._plugins[name] = instance
        logger.info("Plugin loaded: %s v%s", name, instance.meta.version)
        return instance

    def unregister(self, name: str) -> None:
        """Deactivate and remove a plugin by name."""
        plugin = self._plugins.pop(name, None)
        if plugin:
            plugin.deactivate()
            logger.info("Plugin unloaded: %s", name)

    def get(self, name: str) -> Optional[BasePlugin]:
        """Look up a plugin by name."""
        return self._plugins.get(name)

    @property
    def loaded(self) -> list[str]:
        """Names of all currently loaded plugins."""
        return list(self._plugins.keys())

    def shutdown(self) -> None:
        """Deactivate all plugins in reverse-load order."""
        for name in reversed(list(self._plugins)):
            self.unregister(name)
