"""Deterministic routing for base, project, and short-term memory."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from .config import load_config
from .models import MemoryCandidate, MemoryEvent, ProjectRecord
from .project_registry import ensure_project
from .utils import (
    BASE_FIELDS,
    coerce_int,
    derive_summary,
    derive_title,
    iso_now,
    normalize_field,
    normalize_memory_type,
    normalize_project_module,
    normalize_short_subtype,
    safe_relpath,
    slugify,
)


@dataclass
class RouteDecision:
    memory_type: str
    field: str | None
    module: str | None
    subtype: str | None
    target_path: str
    project: ProjectRecord | None
    status: str
    update_mode: str
    note_kind: str


def _timestamp_prefix(created_at: str) -> str:
    clean = created_at.replace("-", "").replace(":", "").replace("T", "_")
    if "+" in clean:
        clean = clean.split("+", 1)[0]
    if "-" in clean[15:]:
        clean = clean.split("-", 1)[0]
    date_part, time_part = clean.split("_", 1)
    return f"{date_part[:8]}_{time_part[:6]}"


def _entry_path(root: Path, base_dir: Path, created_at: str, title: str) -> str:
    filename = f"{_timestamp_prefix(created_at)}_{slugify(title)}.md"
    return safe_relpath(base_dir / filename, root)


def _fallback_project_path(root: Path, project: ProjectRecord, created_at: str, title: str, content: str) -> tuple[str, str]:
    project_dir = Path(project.path)
    lower = content.lower()
    if "?" in content or "待确认" in content or "please confirm" in lower:
        return safe_relpath(project_dir / "open_questions.md", root), "marker"
    return _entry_path(root, project_dir / "research" / "notes", created_at, title), "entry"


def decide_route(root: Path, candidate: MemoryCandidate) -> RouteDecision:
    config = load_config(root)
    created_at = iso_now()
    title = candidate.title or derive_title(candidate.content, candidate.summary)
    memory_type = normalize_memory_type(candidate.memory_type)
    field = normalize_field(candidate.field)
    module = normalize_project_module(candidate.module)
    subtype = normalize_short_subtype(candidate.subtype)

    if memory_type == "base_memory":
        if field in BASE_FIELDS:
            target_path = config["routing"]["base_memory"].get(field, BASE_FIELDS[field])
            return RouteDecision(
                memory_type="base_memory",
                field=field,
                module=None,
                subtype=None,
                target_path=target_path,
                project=None,
                status=candidate.status or "active",
                update_mode=candidate.update_mode or "append",
                note_kind="marker",
            )
        subtype = "needs_review"
        memory_type = "short_term_memory"

    project: ProjectRecord | None = None
    if memory_type == "project_memory" or candidate.project_name:
        allow_create = bool(config["auto_trigger"].get("allow_auto_create_project", True))
        project = ensure_project(root, candidate.project_name, allow_create=allow_create)
        if project is not None:
            project_dir = Path(project.path)
            module = module or "research"
            mapping = config["routing"]["project_memory"]
            note_kind = "entry"
            if module == "research":
                target_path = _entry_path(root, project_dir / "research" / "notes", created_at, title)
            elif module == "analysis":
                target_path = _entry_path(root, project_dir / "analysis" / "outputs", created_at, title)
            elif module == "tools":
                target_path = _entry_path(root, project_dir / "tools" / "specs", created_at, title)
            elif module == "references":
                target_path = _entry_path(root, project_dir / "references", created_at, title)
            elif module == "deliverables":
                target_path = _entry_path(root, project_dir / "deliverables", created_at, title)
            elif module == "decisions":
                target_path = safe_relpath(project_dir / mapping["decisions"], root)
                note_kind = "marker"
            elif module == "questions":
                target_path = safe_relpath(project_dir / mapping["questions"], root)
                note_kind = "marker"
            else:
                target_path, note_kind = _fallback_project_path(root, project, created_at, title, candidate.content)
                if note_kind == "marker":
                    module = "questions"
                else:
                    module = "research"
            return RouteDecision(
                memory_type="project_memory",
                field=None,
                module=module,
                subtype=None,
                target_path=target_path,
                project=project,
                status=candidate.status or "active",
                update_mode=candidate.update_mode or "append",
                note_kind=note_kind,
            )
        subtype = "needs_review"
        memory_type = "short_term_memory"

    subtype = subtype or normalize_short_subtype(candidate.module) or normalize_short_subtype(candidate.field) or "needs_review"
    short_mapping = config["routing"]["short_term"]
    target = short_mapping.get(subtype, short_mapping["default"])
    if target.endswith(".md"):
        target_path = target
        note_kind = "marker"
    else:
        target_path = _entry_path(root, root / target, created_at, title)
        note_kind = "entry"
    status = candidate.status or ("pending_review" if subtype == "needs_review" or target_path.endswith("inbox.md") else "active")
    return RouteDecision(
        memory_type="short_term_memory",
        field=None,
        module=None,
        subtype=subtype,
        target_path=target_path,
        project=None,
        status=status,
        update_mode=candidate.update_mode or "append",
        note_kind=note_kind,
    )


def build_event(root: Path, candidate: MemoryCandidate) -> tuple[MemoryEvent, RouteDecision]:
    route = decide_route(root, candidate)
    created_at = iso_now()
    summary = candidate.summary or derive_summary(candidate.content)
    title = candidate.title or derive_title(candidate.content, summary)
    project = route.project
    event = MemoryEvent(
        memory_id=str(uuid.uuid4()),
        created_at=created_at,
        updated_at=created_at,
        memory_type=route.memory_type,
        title=title,
        summary=summary,
        content=candidate.content.strip(),
        project_name=project.project_name if project else candidate.project_name,
        project_id=project.project_id if project else None,
        field=route.field,
        module=route.module,
        subtype=route.subtype,
        field_or_module=route.field or route.module or route.subtype,
        tags=sorted(set(candidate.tags)),
        importance=coerce_int(candidate.importance),
        confidence=coerce_int(candidate.confidence),
        source=candidate.source or "manual",
        privacy_level=candidate.privacy_level or "local_private",
        status=route.status,
        update_mode=route.update_mode,
        target_path=route.target_path,
        links=list(candidate.links),
        session_id=candidate.session_id,
        turn_id=candidate.turn_id,
        source_event_id=candidate.source_event_id,
        content_hash="",
    )
    return event, route
