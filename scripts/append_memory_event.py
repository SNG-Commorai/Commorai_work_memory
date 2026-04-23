#!/usr/bin/env python3
"""Append a memory event and write it into the appropriate local layer."""

from __future__ import annotations

import argparse
import json
import re
import uuid
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def normalize_memory_type(raw: str | None) -> str:
    mapping = {
        "base": "base_memory",
        "base_memory": "base_memory",
        "project": "project_memory",
        "project_memory": "project_memory",
        "short": "short_term_memory",
        "short_term_memory": "short_term_memory",
    }
    return mapping.get((raw or "").strip().lower(), "short_term_memory")


def ensure_project_dir(root: Path, project_name: str) -> Path:
    slug = slugify(project_name)
    projects_dir = root / "02_Project_Memory"
    projects_dir.mkdir(parents=True, exist_ok=True)

    for child in sorted(projects_dir.iterdir()):
        if child.is_dir() and child.name.endswith(f"_{slug}"):
            return child

    project_id = f"P_{datetime.now().strftime('%Y%m%d')}_{slug}"
    project_dir = projects_dir / project_id
    project_dir.mkdir(parents=True, exist_ok=False)
    for subdir in ["research", "analysis", "tools", "data", "references", "deliverables", "archive"]:
        (project_dir / subdir).mkdir(parents=True, exist_ok=True)
    (project_dir / "project_meta.yaml").write_text(
        (
            f"project_id: {project_id}\n"
            f"project_name: {project_name}\n"
            f"project_slug: {slug}\n"
            f"created_at: {datetime.now().astimezone().isoformat()}\n"
            f"updated_at: {datetime.now().astimezone().isoformat()}\n"
            "status: active\n"
            "stage: planning\n"
            "tags: []\n"
            "privacy_level: local_private\n"
            "summary:\n"
        ),
        encoding="utf-8",
    )
    (project_dir / "project_brief.md").write_text("# Project Brief\n", encoding="utf-8")
    (project_dir / "memory_log.md").write_text("# Project Memory Log\n\n## Entries\n", encoding="utf-8")
    (project_dir / "decisions.md").write_text("# Decision Log\n\n## Decisions\n", encoding="utf-8")
    (project_dir / "open_questions.md").write_text("# Open Questions\n\n## Questions\n", encoding="utf-8")
    return project_dir


def append_text(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        existing = target.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    else:
        existing = ""
    target.write_text(existing + content, encoding="utf-8")


def write_base_memory(root: Path, event: dict[str, object]) -> Path:
    field = str(event.get("field") or "general")
    target = root / "01_Base_Memory" / f"{slugify(field).replace('-', '_')}.md"
    body = (
        f"\n## {event['created_at']} - {field}\n\n"
        f"- Importance: {event['importance']}\n"
        f"- Confidence: {event['confidence']}\n"
        f"- Tags: {', '.join(event['tags']) or 'none'}\n"
        f"- Source: {event['source']}\n"
        f"- Privacy Level: {event['privacy_level']}\n\n"
        f"{event['content']}\n"
    )
    append_text(target, body)
    return target


def write_project_memory(root: Path, event: dict[str, object]) -> Path:
    project_name = str(event.get("project_name") or "").strip()
    if not project_name:
        event["memory_type"] = "short_term_memory"
        return write_short_term_memory(root, event)

    project_dir = ensure_project_dir(root, project_name)
    module = str(event.get("module") or "general")
    entry = (
        f"\n### {event['created_at']} - {module}\n\n"
        f"- Type: entry\n"
        f"- Module: {module}\n"
        f"- Tags: {', '.join(event['tags']) or 'none'}\n"
        f"- Importance: {event['importance']}\n"
        f"- Confidence: {event['confidence']}\n"
        f"- Content: {event['content']}\n"
        f"- Source: {event['source']}\n"
    )
    append_text(project_dir / "memory_log.md", entry)
    return project_dir / "memory_log.md"


def write_short_term_memory(root: Path, event: dict[str, object]) -> Path:
    target = root / "03_Short_Term_Memory" / "inbox.md"
    subtype = str(event.get("module") or event.get("field") or "unsorted")
    body = (
        f"\n## {event['created_at']} - {subtype}\n\n"
        f"- Related project: {event.get('project_name') or 'none'}\n"
        f"- Tags: {', '.join(event['tags']) or 'none'}\n"
        f"- Importance: {event['importance']}\n"
        f"- Confidence: {event['confidence']}\n"
        f"- Privacy Level: {event['privacy_level']}\n"
        f"- Content: {event['content']}\n"
    )
    append_text(target, body)
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a memory event.")
    parser.add_argument("--memory-type", default="short_term_memory")
    parser.add_argument("--content", required=True, help="Memory content to write.")
    parser.add_argument("--project-name")
    parser.add_argument("--field")
    parser.add_argument("--module")
    parser.add_argument("--tags", default="", help="Comma-separated tags.")
    parser.add_argument("--importance", type=int, default=3)
    parser.add_argument("--confidence", type=int, default=3)
    parser.add_argument("--source", default="manual")
    parser.add_argument("--privacy-level", default="local_private")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root. Defaults to the current repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    memory_type = normalize_memory_type(args.memory_type)
    now = datetime.now().astimezone().isoformat()
    tags = [item.strip() for item in args.tags.split(",") if item.strip()]

    event = {
        "event_id": str(uuid.uuid4()),
        "created_at": now,
        "memory_type": memory_type,
        "project_name": args.project_name,
        "field": args.field,
        "module": args.module,
        "tags": tags,
        "importance": min(max(args.importance, 1), 5),
        "confidence": min(max(args.confidence, 1), 5),
        "content": args.content,
        "source": args.source,
        "privacy_level": args.privacy_level,
    }

    if memory_type == "base_memory":
        target = write_base_memory(root, event)
    elif memory_type == "project_memory":
        target = write_project_memory(root, event)
    else:
        target = write_short_term_memory(root, event)

    log_file = root / "00_System" / "logs" / "memory_events.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    print("Write summary")
    print(f"- event_id: {event['event_id']}")
    print(f"- memory_type: {event['memory_type']}")
    print(f"- target: {target.relative_to(root)}")
    print(f"- log: {log_file.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
