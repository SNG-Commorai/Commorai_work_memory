"""Dataclasses for the local memory runtime."""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Any


@dataclass
class MemoryCandidate:
    content: str
    memory_type: str | None = None
    title: str | None = None
    summary: str | None = None
    project_name: str | None = None
    field: str | None = None
    module: str | None = None
    subtype: str | None = None
    tags: list[str] = dc_field(default_factory=list)
    importance: int = 3
    confidence: int = 3
    source: str = "manual"
    privacy_level: str = "local_private"
    status: str | None = None
    update_mode: str | None = None
    links: list[str] = dc_field(default_factory=list)
    session_id: str | None = None
    turn_id: str | None = None
    source_event_id: str | None = None


@dataclass
class TurnContext:
    session_id: str | None = None
    turn_id: str | None = None
    active_project: str | None = None
    user_text: str = ""
    assistant_text: str = ""
    tool_outputs: list[str] = dc_field(default_factory=list)
    candidates: list[dict[str, Any]] = dc_field(default_factory=list)


@dataclass
class ProjectRecord:
    project_id: str
    project_name: str
    project_slug: str
    path: str
    status: str = "active"
    stage: str = "planning"
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class MemoryEvent:
    memory_id: str
    created_at: str
    updated_at: str
    memory_type: str
    title: str
    summary: str
    content: str
    project_name: str | None
    project_id: str | None
    field: str | None
    module: str | None
    subtype: str | None
    field_or_module: str | None
    tags: list[str]
    importance: int
    confidence: int
    source: str
    privacy_level: str
    status: str
    update_mode: str
    target_path: str
    links: list[str]
    session_id: str | None
    turn_id: str | None
    source_event_id: str | None
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "memory_type": self.memory_type,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "project_name": self.project_name,
            "project_id": self.project_id,
            "field": self.field,
            "module": self.module,
            "subtype": self.subtype,
            "field_or_module": self.field_or_module,
            "tags": self.tags,
            "importance": self.importance,
            "confidence": self.confidence,
            "source": self.source,
            "privacy_level": self.privacy_level,
            "status": self.status,
            "update_mode": self.update_mode,
            "target_path": self.target_path,
            "links": self.links,
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "source_event_id": self.source_event_id,
            "content_hash": self.content_hash,
        }


@dataclass
class WriteResult:
    event: MemoryEvent
    target_path: str
    log_path: str
    duplicate_of: str | None = None
    conflict_with: str | None = None

    @property
    def status(self) -> str:
        return self.event.status
