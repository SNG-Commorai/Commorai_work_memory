"""Persistence layer for the local memory runtime."""

from __future__ import annotations

import json
from pathlib import Path

from .config import load_config
from .marker_io import append_text_atomic, atomic_write_text, best_effort_lock, insert_between_markers, read_text
from .models import MemoryEvent, ProjectRecord
from .project_registry import touch_project_updated_at
from .utils import iso_now


def render_entry_document(event: MemoryEvent) -> str:
    tags = ", ".join(event.tags) if event.tags else "none"
    field_or_module = event.field_or_module or "none"
    project_name = event.project_name or "none"
    return (
        f"# {event.title}\n\n"
        f"- Created At: {event.created_at}\n"
        f"- Updated At: {event.updated_at}\n"
        f"- Memory ID: {event.memory_id}\n"
        f"- Memory Type: {event.memory_type}\n"
        f"- Field/Module: {field_or_module}\n"
        f"- Importance: {event.importance}\n"
        f"- Confidence: {event.confidence}\n"
        f"- Status: {event.status}\n"
        f"- Tags: {tags}\n"
        f"- Related Project: {project_name}\n"
        f"- Target Path: {event.target_path}\n\n"
        f"## Summary\n{event.summary}\n\n"
        f"## Content\n{event.content.rstrip()}\n"
    )


def render_marker_block(event: MemoryEvent) -> str:
    tags = ", ".join(event.tags) if event.tags else "none"
    return (
        f"### {event.title}\n"
        f"- Memory ID: `{event.memory_id}`\n"
        f"- Updated At: {event.updated_at}\n"
        f"- Source: {event.source}\n"
        f"- Status: {event.status}\n"
        f"- Tags: {tags}\n"
        f"- Summary: {event.summary}\n\n"
        f"{event.content.rstrip()}\n"
    )


def render_project_log_block(event: MemoryEvent) -> str:
    tags = ", ".join(event.tags) if event.tags else "none"
    return (
        f"- [{event.updated_at}] `{event.module or event.subtype or event.field_or_module or 'general'}`"
        f" | `{event.title}` | `{event.target_path}` | tags: {tags}\n"
    )


def render_conflict_block(new_event: MemoryEvent, old_event: MemoryEvent) -> str:
    return (
        f"### Conflict: {new_event.title}\n"
        f"- Recorded At: {new_event.updated_at}\n"
        f"- Field: {new_event.field}\n"
        f"- Existing Memory: `{old_event.memory_id}` @ `{old_event.target_path}`\n"
        f"- Incoming Memory: `{new_event.memory_id}`\n"
        f"- Existing Summary: {old_event.summary}\n"
        f"- Incoming Summary: {new_event.summary}\n"
        f"- Action: Review manually before promoting or replacing.\n\n"
        f"#### Existing Content\n{old_event.content.rstrip()}\n\n"
        f"#### Incoming Content\n{new_event.content.rstrip()}\n"
    )


def _write_event_doc(path: Path, event: MemoryEvent) -> None:
    atomic_write_text(path, render_entry_document(event))


def _append_log(path: Path, event: MemoryEvent) -> None:
    insert_between_markers(path, render_project_log_block(event))


def _append_operation_line(path: Path, line: str) -> None:
    content = read_text(path)
    if "## Logs" in content:
        insert_between_markers(path, line)
        return
    append_text_atomic(path, line)


def ensure_operation_log(root: Path) -> Path:
    config = load_config(root)
    path = root / config["files"]["operation_log"]
    if not path.exists():
        atomic_write_text(
            path,
            "# Operation Log\n\nRecords memory runtime operations.\n\n## Logs\n",
        )
    return path


def _project_root_from_target(event: MemoryEvent) -> Path | None:
    parts = Path(event.target_path).parts
    if len(parts) >= 2 and parts[0] == "02_Project_Memory":
        return Path(parts[0]) / parts[1]
    return None


def write_event(root: Path, event: MemoryEvent) -> MemoryEvent:
    target = root / event.target_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if event.memory_type == "base_memory":
        insert_between_markers(target, render_marker_block(event))
        if event.target_path not in event.links:
            event.links.append(event.target_path)
    elif event.memory_type == "project_memory":
        if event.module in {"decisions", "questions"} and target.suffix == ".md":
            insert_between_markers(target, render_marker_block(event))
        else:
            _write_event_doc(target, event)
        project_root = _project_root_from_target(event)
        if project_root is not None:
            memory_log_rel = (project_root / "memory_log.md").as_posix()
            memory_log = root / memory_log_rel
            _append_log(memory_log, event)
            for link in [event.target_path, memory_log_rel]:
                if link not in event.links:
                    event.links.append(link)
    else:
        if target.name == "inbox.md":
            insert_between_markers(target, render_marker_block(event))
        else:
            _write_event_doc(target, event)
        if event.target_path not in event.links:
            event.links.append(event.target_path)
    return event


def write_conflict(root: Path, event: MemoryEvent, old_event: MemoryEvent) -> None:
    config = load_config(root)
    conflict_path = root / config["routing"]["base_memory"]["conflicts"]
    insert_between_markers(conflict_path, render_conflict_block(event, old_event))


def append_event_log(root: Path, event: MemoryEvent) -> Path:
    config = load_config(root)
    log_path = root / config["files"]["event_log"]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with best_effort_lock(log_path):
        existing = read_text(log_path)
        if existing and not existing.endswith("\n"):
            existing += "\n"
        existing += json.dumps(event.to_dict(), ensure_ascii=False) + "\n"
        atomic_write_text(log_path, existing)
    return log_path


def append_operation_log(root: Path, action: str, detail: str) -> Path:
    path = ensure_operation_log(root)
    line = f"- [{iso_now()}] `{action}`: {detail}\n"
    with best_effort_lock(path):
        _append_operation_line(path, line)
    return path


def touch_project(root: Path, project: ProjectRecord | None) -> ProjectRecord | None:
    if project is None:
        return None
    return touch_project_updated_at(root, project)
