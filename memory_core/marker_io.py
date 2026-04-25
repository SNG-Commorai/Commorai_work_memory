"""Atomic file operations and marker-safe insertion helpers."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


START_MARKER = "<!-- MEMORY_CONTENT_START -->"
END_MARKER = "<!-- MEMORY_CONTENT_END -->"
PLACEHOLDER_TEXTS = {
    "No records yet.",
    "No formal entries yet.",
    "No pending items.",
}


@contextmanager
def best_effort_lock(path: Path) -> Iterator[None]:
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+", encoding="utf-8")
    try:
        try:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        except (ImportError, OSError):
            try:
                import msvcrt  # type: ignore

                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)  # type: ignore[attr-defined]
            except (ImportError, OSError):
                pass
        yield
    finally:
        try:
            try:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except (ImportError, OSError):
                try:
                    import msvcrt  # type: ignore

                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)  # type: ignore[attr-defined]
                except (ImportError, OSError):
                    pass
        finally:
            handle.close()


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as temp:
        temp.write(content)
        temp.flush()
        os.fsync(temp.fileno())
        temp_path = Path(temp.name)
    os.replace(temp_path, path)


def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def append_text_atomic(path: Path, block: str) -> None:
    existing = read_text(path)
    if existing and not existing.endswith("\n"):
        existing += "\n"
    content = existing + block
    if content and not content.endswith("\n"):
        content += "\n"
    atomic_write_text(path, content)


def insert_between_markers(path: Path, block: str) -> None:
    block = block.strip()
    existing = read_text(path)
    if START_MARKER in existing and END_MARKER in existing:
        before, remainder = existing.split(START_MARKER, 1)
        middle, after = remainder.split(END_MARKER, 1)
        inner = middle.strip()
        existing_entries = ""
        if inner and inner not in PLACEHOLDER_TEXTS:
            existing_entries = inner
        new_middle = "\n"
        if block:
            new_middle += block + "\n"
        if existing_entries:
            new_middle += "\n" + existing_entries + "\n"
        atomic_write_text(path, before + START_MARKER + new_middle + END_MARKER + after)
        return
    append_text_atomic(path, block + "\n")


def write_json_atomic(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default
