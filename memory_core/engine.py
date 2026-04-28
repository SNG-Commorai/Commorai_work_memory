"""Orchestration layer for extraction, routing, dedupe, persistence, and indexing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import load_config
from .dedupe import compute_content_hash, find_base_conflict, find_duplicate, rebuild_hash_store, record_hash
from .extractor import extract_candidates
from .indexers import rebuild_all_indexes
from .marker_io import atomic_write_text, best_effort_lock
from .models import MemoryCandidate, MemoryEvent, TurnContext, WriteResult
from .project_registry import create_project, ensure_project
from .router import build_event
from .utils import (
    BASE_FIELDS,
    coerce_int,
    derive_summary,
    derive_title,
    ensure_list,
    iso_now,
    normalize_field,
    normalize_memory_type,
    normalize_project_module,
    normalize_short_subtype,
    safe_relpath,
)
from .writers import append_event_log, touch_project, write_conflict, write_event


def load_canonical_events(root: Path) -> list[MemoryEvent]:
    config = load_config(root)
    log_path = root / config["files"]["event_log"]
    if not log_path.exists():
        return []
    events: list[MemoryEvent] = []
    for raw_line in log_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        event = canonicalize_record(root, record)
        events.append(event)
    return events


def canonicalize_record(root: Path, record: dict[str, Any]) -> MemoryEvent:
    memory_type = normalize_memory_type(record.get("memory_type"))
    created_at = str(record.get("created_at") or iso_now())
    updated_at = str(record.get("updated_at") or created_at)
    content = str(record.get("content") or "").strip()
    summary = str(record.get("summary") or derive_summary(content))
    title = str(record.get("title") or derive_title(content, summary))
    field = normalize_field(record.get("field"))
    module_hint = record.get("module")
    subtype_hint = record.get("subtype")
    if memory_type == "project_memory" and not module_hint:
        module_hint = record.get("field_or_module")
    if memory_type == "short_term_memory" and not subtype_hint:
        subtype_hint = record.get("field_or_module")
    module = normalize_project_module(module_hint)
    subtype = normalize_short_subtype(subtype_hint)
    target_path = str(record.get("target_path") or infer_target_path(root, memory_type, field, module, subtype, record))
    event = MemoryEvent(
        memory_id=str(record.get("memory_id") or record.get("event_id") or record.get("id") or ""),
        created_at=created_at,
        updated_at=updated_at,
        memory_type=memory_type,
        title=title,
        summary=summary,
        content=content,
        project_name=record.get("project_name"),
        project_id=record.get("project_id"),
        field=field if memory_type == "base_memory" else None,
        module=module if memory_type == "project_memory" else None,
        subtype=subtype if memory_type == "short_term_memory" else None,
        field_or_module=str(record.get("field_or_module") or field or module or subtype or ""),
        tags=ensure_list(record.get("tags")),
        importance=coerce_int(record.get("importance")),
        confidence=coerce_int(record.get("confidence")),
        source=str(record.get("source") or "migration"),
        privacy_level=str(record.get("privacy_level") or "local_private"),
        status=str(record.get("status") or ("pending_review" if memory_type == "short_term_memory" else "active")),
        update_mode=str(record.get("update_mode") or "append"),
        target_path=target_path,
        links=ensure_list(record.get("links")),
        session_id=record.get("session_id"),
        turn_id=record.get("turn_id"),
        source_event_id=str(record.get("source_event_id") or record.get("event_id") or "") or None,
        content_hash=str(record.get("content_hash") or ""),
    )
    if not event.memory_id:
        event.memory_id = str(record.get("event_id") or record.get("source_event_id") or title)
    if not event.content_hash:
        event.content_hash = compute_content_hash(event)
    if not event.field_or_module:
        event.field_or_module = event.field or event.module or event.subtype
    return event


def infer_target_path(
    root: Path,
    memory_type: str,
    field: str | None,
    module: str | None,
    subtype: str | None,
    record: dict[str, Any],
) -> str:
    config = load_config(root)
    if memory_type == "base_memory" and field in BASE_FIELDS:
        return config["routing"]["base_memory"][field]
    if memory_type == "project_memory":
        links = ensure_list(record.get("links"))
        for link in links:
            if link.endswith(".md") and "memory_log.md" not in link:
                return link
        project = ensure_project(root, record.get("project_name"), allow_create=False)
        if project is not None:
            project_root = Path(project.path)
            if module == "research":
                return safe_relpath(project_root / "memory_log.md", root) if not record.get("target_path") else str(record["target_path"])
            if module == "analysis":
                return safe_relpath(project_root / "memory_log.md", root) if not record.get("target_path") else str(record["target_path"])
            if module == "tools":
                return safe_relpath(project_root / "memory_log.md", root) if not record.get("target_path") else str(record["target_path"])
            if module == "decisions":
                return safe_relpath(project_root / "decisions.md", root)
            if module == "questions":
                return safe_relpath(project_root / "open_questions.md", root)
            return safe_relpath(project_root / "memory_log.md", root)
    short_mapping = config["routing"]["short_term"]
    if subtype and subtype in short_mapping:
        target = short_mapping[subtype]
        if target.endswith(".md"):
            return target
    return short_mapping["default"]


def persist_candidate(root: Path, candidate: MemoryCandidate) -> WriteResult:
    existing_events = load_canonical_events(root)
    event, route = build_event(root, candidate)
    event.content_hash = compute_content_hash(event)

    duplicate = find_duplicate(root, event)
    if duplicate is None:
        for existing in existing_events:
            if existing.content_hash == event.content_hash:
                duplicate = {
                    "memory_id": existing.memory_id,
                    "target_path": existing.target_path,
                    "status": existing.status,
                    "updated_at": existing.updated_at,
                }
                break
    if duplicate is not None:
        event.status = "duplicate_skipped"
        event.update_mode = "noop"
        if duplicate.get("target_path"):
            event.target_path = duplicate["target_path"]
        if duplicate.get("target_path") and duplicate["target_path"] not in event.links:
            event.links.append(duplicate["target_path"])
        log_path = append_event_log(root, event)
        return WriteResult(event=event, target_path=event.target_path, log_path=safe_relpath(log_path, root), duplicate_of=duplicate.get("memory_id"))

    conflict = find_base_conflict(root, event, existing_events)
    if conflict is not None:
        event.status = "conflict_recorded"
        event.update_mode = "conflict_only"
        event.target_path = "01_Base_Memory/conflicts.md"
        event.links = [event.target_path]
        write_conflict(root, event, conflict)
        log_path = append_event_log(root, event)
        record_hash(root, event)
        rebuild_all_indexes(root, load_canonical_events(root))
        return WriteResult(event=event, target_path=event.target_path, log_path=safe_relpath(log_path, root), conflict_with=conflict.memory_id)

    write_event(root, event)
    if route.project is not None:
        touch_project(root, route.project)
    log_path = append_event_log(root, event)
    record_hash(root, event)
    rebuild_all_indexes(root, load_canonical_events(root))
    return WriteResult(event=event, target_path=event.target_path, log_path=safe_relpath(log_path, root))


def add_manual_memory(
    root: Path,
    *,
    content: str,
    memory_type: str,
    project_name: str | None = None,
    field: str | None = None,
    module: str | None = None,
    subtype: str | None = None,
    title: str | None = None,
    summary: str | None = None,
    tags: list[str] | None = None,
    importance: int = 3,
    confidence: int = 3,
    source: str = "manual",
    privacy_level: str = "local_private",
    session_id: str | None = None,
    turn_id: str | None = None,
) -> WriteResult:
    candidate = MemoryCandidate(
        content=content,
        memory_type=memory_type,
        project_name=project_name,
        field=field,
        module=module,
        subtype=subtype,
        title=title,
        summary=summary,
        tags=tags or [],
        importance=importance,
        confidence=confidence,
        source=source,
        privacy_level=privacy_level,
        session_id=session_id,
        turn_id=turn_id,
    )
    return persist_candidate(root, candidate)


def process_turn(turn_ctx: TurnContext, root: Path) -> list[WriteResult]:
    candidates = extract_candidates(turn_ctx)
    results = [persist_candidate(root, candidate) for candidate in candidates]
    return results


def rebuild_indexes(root: Path) -> dict[str, list[str] | str]:
    events = load_canonical_events(root)
    rebuild_hash_store(root, events)
    return rebuild_all_indexes(root, events)


def review_short(root: Path) -> dict[str, list[dict[str, str]]]:
    suggestions: list[dict[str, str]] = []
    short_root = root / "03_Short_Term_Memory"
    for path in sorted(short_root.rglob("*.md")):
        if path.name in {"README.md", "short_index.md"}:
            continue
        relative = safe_relpath(path, root)
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        suggestion = "keep_short_term"
        if "prefer " in lower or "原则" in text:
            suggestion = "candidate_base_memory"
        elif "project" in lower or "项目" in text:
            suggestion = "candidate_project_memory"
        suggestions.append({"path": relative, "suggestion": suggestion})
    return {"items": suggestions}


def migrate_legacy(root: Path) -> dict[str, Any]:
    config = load_config(root)
    log_path = root / config["files"]["event_log"]
    if not log_path.exists():
        rebuild_all_indexes(root, [])
        return {"migrated": 0, "log_path": safe_relpath(log_path, root)}
    original = log_path.read_text(encoding="utf-8").splitlines()
    canonical_events = []
    for line in original:
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        event = canonicalize_record(root, record)
        event.source = "migration" if event.source == "manual" and "memory_id" not in record else event.source
        event.update_mode = "migrate" if "memory_id" not in record or "updated_at" not in record or "target_path" not in record else event.update_mode
        canonical_events.append(event)
    backup_path = log_path.with_name(f"{log_path.stem}.legacy_backup.jsonl")
    if original:
        atomic_write_text(backup_path, "\n".join(original) + "\n")
    payload = "\n".join(json.dumps(event.to_dict(), ensure_ascii=False) for event in canonical_events)
    if payload:
        payload += "\n"
    with best_effort_lock(log_path):
        atomic_write_text(log_path, payload)
    rebuild_hash_store(root, canonical_events)
    rebuild_all_indexes(root, canonical_events)
    return {
        "migrated": len(canonical_events),
        "log_path": safe_relpath(log_path, root),
        "backup_path": safe_relpath(backup_path, root),
    }


def create_project_space(root: Path, project_name: str, stage: str = "planning") -> dict[str, str]:
    record = create_project(root, project_name, stage=stage)
    rebuild_project = rebuild_all_indexes(root, load_canonical_events(root))
    return {
        "project_id": record.project_id,
        "project_name": record.project_name,
        "path": safe_relpath(Path(record.path), root),
        "stage": record.stage,
        "project_index": str(rebuild_project["project_index"]),
    }
