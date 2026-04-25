"""Content hash dedupe and base-memory conflict detection."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .config import load_config
from .marker_io import best_effort_lock, load_json, write_json_atomic
from .models import MemoryEvent
from .utils import compact_text, slugify


def compute_content_hash(event: MemoryEvent) -> str:
    material = "||".join(
        [
            compact_text(event.content),
            event.memory_type or "",
            event.project_name or "",
            event.field or "",
            event.module or "",
            event.subtype or "",
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def hash_store_path(root: Path) -> Path:
    config = load_config(root)
    return root / config["files"]["content_hashes"]


def load_hash_store(root: Path) -> dict[str, dict[str, str]]:
    return load_json(hash_store_path(root), {})


def find_duplicate(root: Path, event: MemoryEvent) -> dict[str, str] | None:
    store = load_hash_store(root)
    return store.get(event.content_hash)


def record_hash(root: Path, event: MemoryEvent) -> None:
    path = hash_store_path(root)
    with best_effort_lock(path):
        store = load_json(path, {})
        store[event.content_hash] = {
            "memory_id": event.memory_id,
            "target_path": event.target_path,
            "status": event.status,
            "updated_at": event.updated_at,
        }
        write_json_atomic(path, store)


def rebuild_hash_store(root: Path, events: list[MemoryEvent]) -> None:
    path = hash_store_path(root)
    payload = {
        event.content_hash: {
            "memory_id": event.memory_id,
            "target_path": event.target_path,
            "status": event.status,
            "updated_at": event.updated_at,
        }
        for event in events
        if event.content_hash
    }
    with best_effort_lock(path):
        write_json_atomic(path, payload)


def find_base_conflict(root: Path, event: MemoryEvent, events: list[MemoryEvent]) -> MemoryEvent | None:
    if event.memory_type != "base_memory" or not event.field:
        return None
    target_slug = slugify(event.title or event.summary, fallback="memory")
    for existing in reversed(events):
        if existing.memory_type != "base_memory":
            continue
        if existing.field != event.field:
            continue
        existing_slug = slugify(existing.title or existing.summary, fallback="memory")
        if existing_slug == target_slug and existing.content_hash != event.content_hash:
            return existing
    return None
