"""Task templates — reusable blueprints for common task patterns.

Templates define pre-filled field values and support variable
interpolation using ``{variable_name}`` placeholders.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from task_manager.models import Task, Priority


@dataclass
class TaskTemplate:
    """A reusable task blueprint.

    Attributes:
        name: Unique template identifier.
        title_pattern: Title with ``{var}`` placeholders.
        description_pattern: Description with ``{var}`` placeholders.
        default_priority: Priority assigned by default.
        default_tags: Tags to attach to every generated task.
        subtask_titles: Pre-defined subtask titles.
        variables: Mapping of variable name → default value.
    """

    name: str
    title_pattern: str
    description_pattern: str = ""
    default_priority: Priority = Priority.MEDIUM
    default_tags: list[str] = field(default_factory=list)
    subtask_titles: list[str] = field(default_factory=list)
    variables: dict[str, str] = field(default_factory=dict)

    def render(self, overrides: Optional[dict[str, str]] = None) -> Task:
        """Create a Task instance from the template.

        Args:
            overrides: Variable values that override the defaults.

        Returns:
            A new Task with the template's fields applied.
        """
        vars_ = {**self.variables, **(overrides or {})}
        title = self.title_pattern.format(**vars_)
        description = self.description_pattern.format(**vars_)

        task = Task(
            title=title,
            description=description,
            priority=self.default_priority,
            tags=list(self.default_tags),
        )
        for st_title in self.subtask_titles:
            task.add_subtask(st_title.format(**vars_))

        return task

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "title_pattern": self.title_pattern,
            "description_pattern": self.description_pattern,
            "default_priority": self.default_priority.value,
            "default_tags": self.default_tags,
            "subtask_titles": self.subtask_titles,
            "variables": self.variables,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskTemplate:
        return cls(
            name=data["name"],
            title_pattern=data["title_pattern"],
            description_pattern=data.get("description_pattern", ""),
            default_priority=Priority(data.get("default_priority", 2)),
            default_tags=data.get("default_tags", []),
            subtask_titles=data.get("subtask_titles", []),
            variables=data.get("variables", {}),
        )


class TemplateRegistry:
    """Store and manage task templates.

    Templates can be registered in-memory or loaded from / saved to a
    JSON file on disk.
    """

    def __init__(self, file_path: Optional[str] = None) -> None:
        self._templates: dict[str, TaskTemplate] = {}
        self._path = Path(file_path) if file_path else None
        if self._path and self._path.exists():
            self._load()

    # ── CRUD ─────────────────────────────────────────────────────

    def add(self, template: TaskTemplate) -> None:
        """Register a template (overwrites if name exists)."""
        self._templates[template.name] = template
        self._persist()

    def get(self, name: str) -> Optional[TaskTemplate]:
        return self._templates.get(name)

    def remove(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            self._persist()
            return True
        return False

    def list_all(self) -> list[TaskTemplate]:
        return list(self._templates.values())

    # ── Built-in templates ───────────────────────────────────────

    @staticmethod
    def builtin_templates() -> list[TaskTemplate]:
        """Return a set of useful built-in templates."""
        return [
            TaskTemplate(
                name="bug-fix",
                title_pattern="Fix: {summary}",
                description_pattern=(
                    "## Bug Report\n\n"
                    "**Steps to reproduce:**\n{steps}\n\n"
                    "**Expected:** {expected}\n\n"
                    "**Actual:** {actual}\n"
                ),
                default_priority=Priority.HIGH,
                default_tags=["bug"],
                subtask_titles=[
                    "Reproduce the issue",
                    "Identify root cause",
                    "Implement fix",
                    "Add regression test",
                    "Code review",
                ],
                variables={
                    "summary": "",
                    "steps": "1. ...",
                    "expected": "",
                    "actual": "",
                },
            ),
            TaskTemplate(
                name="feature",
                title_pattern="Feature: {feature_name}",
                description_pattern=(
                    "## Feature Request\n\n"
                    "**User story:** As a {role}, I want {goal} "
                    "so that {benefit}.\n\n"
                    "**Acceptance criteria:**\n- [ ] {criteria}\n"
                ),
                default_priority=Priority.MEDIUM,
                default_tags=["feature"],
                subtask_titles=[
                    "Design & specification",
                    "Implementation",
                    "Unit tests",
                    "Documentation",
                    "QA review",
                ],
                variables={
                    "feature_name": "",
                    "role": "user",
                    "goal": "",
                    "benefit": "",
                    "criteria": "",
                },
            ),
            TaskTemplate(
                name="release",
                title_pattern="Release v{version}",
                description_pattern=(
                    "## Release Checklist for v{version}\n\n"
                    "Target date: {target_date}\n"
                ),
                default_priority=Priority.CRITICAL,
                default_tags=["release", "ops"],
                subtask_titles=[
                    "Feature freeze",
                    "Run full test suite",
                    "Update changelog",
                    "Bump version",
                    "Tag release",
                    "Deploy to staging",
                    "Deploy to production",
                    "Post-release verification",
                ],
                variables={"version": "0.0.0", "target_date": "TBD"},
            ),
        ]

    # ── Persistence ──────────────────────────────────────────────

    def _load(self) -> None:
        if self._path and self._path.exists():
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._templates = {
                item["name"]: TaskTemplate.from_dict(item) for item in data
            }

    def _persist(self) -> None:
        if self._path:
            out = [t.to_dict() for t in self._templates.values()]
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
