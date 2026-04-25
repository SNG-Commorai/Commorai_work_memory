"""Index generation for base, project, and short-term memory."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .config import load_config
from .marker_io import atomic_write_text
from .models import MemoryEvent
from .project_registry import iter_projects
from .utils import BASE_FIELDS, safe_relpath


def _event_map(events: list[MemoryEvent]) -> dict[str, list[MemoryEvent]]:
    grouped: dict[str, list[MemoryEvent]] = defaultdict(list)
    for event in events:
        grouped[event.target_path].append(event)
    return grouped


def rebuild_base_index(root: Path, events: list[MemoryEvent]) -> Path:
    grouped = _event_map(events)
    lines = [
        "# Base Memory Index",
        "",
        "Auto-generated snapshot of long-term memory field files.",
        "",
        "| File | Field | Entries | Last Updated | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for field_name, relative in BASE_FIELDS.items():
        target = root / relative
        relevant = [item for item in grouped.get(relative, []) if item.status == "active"]
        count = len(relevant)
        latest = max((item.updated_at for item in relevant), default="-")
        status = "Has content" if count else "Pending"
        lines.append(f"| `{target.name}` | `{field_name}` | {count} | {latest} | {status} |")
    conflicts_relative = "01_Base_Memory/conflicts.md"
    conflict_events = [item for item in grouped.get(conflicts_relative, []) if item.status == "conflict_recorded"]
    lines.append(
        f"| `conflicts.md` | `conflicts` | {len(conflict_events)} | "
        f"{max((item.updated_at for item in conflict_events), default='-')} | "
        f"{'Attention needed' if conflict_events else 'Pending'} |"
    )
    path = root / load_config(root)["files"]["base_index"]
    atomic_write_text(path, "\n".join(lines) + "\n")
    return path


def rebuild_short_index(root: Path, events: list[MemoryEvent]) -> Path:
    grouped = _event_map(events)
    inbox_path = "03_Short_Term_Memory/inbox.md"
    inbox_count = len([item for item in grouped.get(inbox_path, []) if item.status != "duplicate_skipped"])
    sections = [
        ("inbox.md", "Default entry", inbox_count),
        ("sparks/", "Inspiration", len(list((root / "03_Short_Term_Memory" / "sparks").glob("*.md")))),
        ("temp_research/", "Temporary research", len(list((root / "03_Short_Term_Memory" / "temp_research").glob("*.md")))),
        ("temp_analysis/", "Temporary analysis", len(list((root / "03_Short_Term_Memory" / "temp_analysis").glob("*.md")))),
        ("tasks/", "Short tasks", len(list((root / "03_Short_Term_Memory" / "tasks").glob("*.md")))),
        ("to_review/", "Needs review", len(list((root / "03_Short_Term_Memory" / "to_review").glob("*.md")))),
    ]
    lines = [
        "# Short-Term Memory Index",
        "",
        "Auto-generated overview of short-term memory buckets.",
        "",
        "| Path | Purpose | Count |",
        "| --- | --- | --- |",
    ]
    for path_text, purpose, count in sections:
        lines.append(f"| `{path_text}` | {purpose} | {count} |")
    path = root / load_config(root)["files"]["short_index"]
    atomic_write_text(path, "\n".join(lines) + "\n")
    return path


def _module_entries(root: Path, project_root: Path, module_dir: str, events: list[MemoryEvent]) -> list[tuple[str, str, str, str]]:
    module_prefix = safe_relpath(project_root / module_dir, root) + "/"
    relevant: list[tuple[str, str, str, str]] = []
    for event in events:
        if not event.target_path.startswith(module_prefix):
            continue
        local_rel = (root / event.target_path).relative_to(project_root).as_posix()
        tags = ", ".join(event.tags) if event.tags else "-"
        relevant.append((local_rel, event.title, event.updated_at, tags))
    deduped: dict[str, tuple[str, str, str, str]] = {}
    for item in relevant:
        deduped[item[0]] = item
    return sorted(deduped.values(), key=lambda value: value[2], reverse=True)


def rebuild_project_module_indexes(root: Path, events: list[MemoryEvent]) -> list[Path]:
    written: list[Path] = []
    for project in iter_projects(root):
        project_path = Path(project.path)
        specs = [
            ("research/notes", project_path / "research" / "research_index.md", "# Research Index"),
            ("analysis/outputs", project_path / "analysis" / "analysis_index.md", "# Analysis Index"),
            ("tools/specs", project_path / "tools" / "tools_index.md", "# Tools Index"),
        ]
        for module_dir, index_path, title in specs:
            entries = _module_entries(root, project_path, module_dir, events)
            lines = [
                title,
                "",
                "| Path | Title | Updated At | Tags |",
                "| --- | --- | --- | --- |",
            ]
            if entries:
                for path_text, entry_title, updated_at, tags in entries:
                    lines.append(f"| `{path_text}` | {entry_title} | {updated_at} | {tags} |")
            else:
                lines.append("| - | - | - | - |")
            atomic_write_text(index_path, "\n".join(lines) + "\n")
            written.append(index_path)
    return written


def rebuild_project_index(root: Path) -> Path:
    lines = [
        "# Project Index",
        "",
        "Auto-generated registry of project memory spaces.",
        "",
        "| Project ID | Project Name | Status | Stage | Updated At | Path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in iter_projects(root):
        lines.append(
            f"| `{record.project_id}` | {record.project_name} | {record.status} | {record.stage} | "
            f"{record.updated_at or '-'} | `{safe_relpath(Path(record.path), root)}` |"
        )
    path = root / load_config(root)["files"]["project_index"]
    atomic_write_text(path, "\n".join(lines) + "\n")
    return path


def rebuild_all_indexes(root: Path, events: list[MemoryEvent]) -> dict[str, list[str] | str]:
    base_index = rebuild_base_index(root, events)
    short_index = rebuild_short_index(root, events)
    project_index = rebuild_project_index(root)
    module_indexes = rebuild_project_module_indexes(root, events)
    return {
        "base_index": safe_relpath(base_index, root),
        "short_index": safe_relpath(short_index, root),
        "project_index": safe_relpath(project_index, root),
        "module_indexes": [safe_relpath(path, root) for path in module_indexes],
    }
