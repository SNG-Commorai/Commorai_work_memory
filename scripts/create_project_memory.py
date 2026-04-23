#!/usr/bin/env python3
"""Create a project memory folder with standard files and subdirectories."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROJECT_MEMORY_DIR = ROOT / "02_Project_Memory"
SUBDIRECTORIES = [
    "research",
    "analysis",
    "tools",
    "data",
    "references",
    "deliverables",
    "archive",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "project"


def project_files(project_name: str, slug: str, timestamp: str) -> dict[str, str]:
    return {
        "project_meta.yaml": (
            f"project_id: P_{timestamp}_{slug}\n"
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
        "project_brief.md": (
            "# Project Brief\n\n"
            "## Project Summary\n\n"
            "## Goals\n\n"
            "## Scope\n\n"
            "## Key Context\n\n"
            "## Current Status\n\n"
            "## Important Links or References\n\n"
            "## Notes\n"
        ),
        "memory_log.md": "# Project Memory Log\n\n## Entries\n",
        "decisions.md": "# Decision Log\n\n## Decisions\n",
        "open_questions.md": "# Open Questions\n\n## Questions\n",
    }


def find_existing_project(project_root: Path, slug: str) -> Path | None:
    if not project_root.exists():
        return None
    pattern = re.compile(rf"^P_\d{{8}}_{re.escape(slug)}$")
    for child in sorted(project_root.iterdir()):
        if child.is_dir() and pattern.match(child.name):
            return child
    return None


def create_project(root: Path, project_name: str) -> tuple[Path, bool]:
    projects_dir = root / "02_Project_Memory"
    projects_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(project_name)
    existing = find_existing_project(projects_dir, slug)
    if existing is not None:
        return existing, False

    timestamp = datetime.now().strftime("%Y%m%d")
    project_dir = projects_dir / f"P_{timestamp}_{slug}"
    project_dir.mkdir(parents=True, exist_ok=False)

    for subdirectory in SUBDIRECTORIES:
        (project_dir / subdirectory).mkdir(parents=True, exist_ok=True)

    for filename, content in project_files(project_name, slug, timestamp).items():
        (project_dir / filename).write_text(content, encoding="utf-8")

    return project_dir, True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a project memory folder.")
    parser.add_argument("project_name", help="Human-readable project name.")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root. Defaults to the current repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir, created = create_project(args.root.resolve(), args.project_name)

    if created:
        print("Created project memory")
    else:
        print("Project memory already exists")

    print(f"- path: {project_dir}")
    print(f"- slug: {project_dir.name.split('_', 2)[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
