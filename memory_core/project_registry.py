"""Project lookup and template-based project creation."""

from __future__ import annotations

import shutil
from pathlib import Path

from .config import load_config
from .marker_io import atomic_write_text
from .models import ProjectRecord
from .utils import iso_now, load_yaml_or_json, slugify


def _project_meta_values(project_name: str, stage: str = "planning") -> dict[str, str]:
    project_slug = slugify(project_name, fallback="project")
    date_part = iso_now()[:10].replace("-", "")
    project_id = f"P_{date_part}_{project_slug}"
    now = iso_now()
    return {
        "project_id": project_id,
        "project_name": project_name,
        "project_slug": project_slug,
        "project_stage": stage,
        "created_at": now,
        "updated_at": now,
    }


def _replace_tokens(text: str, values: dict[str, str]) -> str:
    replaced = text
    replacements = {
        "P_YYYYMMDD_project-slug": values["project_id"],
        "{{project_name}}": values["project_name"],
        "{{project_stage}}": values["project_stage"],
        "project-slug": values["project_slug"],
        "{{created_at}}": values["created_at"],
        "{{updated_at}}": values["updated_at"],
    }
    for old, new in replacements.items():
        replaced = replaced.replace(old, new)
    return replaced


def read_project_meta(project_dir: Path) -> ProjectRecord | None:
    meta_path = project_dir / "project_meta.yaml"
    if not meta_path.exists():
        return None
    data = load_yaml_or_json(meta_path)
    if not data:
        return None
    project_id = str(data.get("project_id") or project_dir.name)
    project_name = str(data.get("project_name") or project_dir.name)
    project_slug = str(data.get("project_slug") or project_dir.name.split("_", 2)[-1])
    return ProjectRecord(
        project_id=project_id,
        project_name=project_name,
        project_slug=project_slug,
        path=str(project_dir),
        status=str(data.get("status") or "active"),
        stage=str(data.get("project_stage") or data.get("stage") or "planning"),
        created_at=str(data.get("created_at") or "") or None,
        updated_at=str(data.get("updated_at") or "") or None,
    )


def iter_projects(root: Path) -> list[ProjectRecord]:
    projects_dir = root / "02_Project_Memory"
    if not projects_dir.exists():
        return []
    records: list[ProjectRecord] = []
    for child in sorted(projects_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        record = read_project_meta(child)
        if record is not None:
            records.append(record)
    return records


def find_project(root: Path, query: str | None) -> ProjectRecord | None:
    if not query:
        return None
    cleaned = query.strip()
    if not cleaned:
        return None
    slug = slugify(cleaned, fallback="project")
    for record in iter_projects(root):
        if record.project_name == cleaned:
            return record
        if record.project_slug == slug:
            return record
        if record.project_id == cleaned:
            return record
    return None


def _ensure_project_directories(project_dir: Path) -> None:
    required = [
        "research/notes",
        "analysis/outputs",
        "tools/specs",
        "data",
        "references",
        "deliverables",
        "archive",
    ]
    for relative in required:
        (project_dir / relative).mkdir(parents=True, exist_ok=True)


def create_project(root: Path, project_name: str, stage: str = "planning") -> ProjectRecord:
    config = load_config(root)
    template_dir = root / config["files"]["project_template"]
    if not template_dir.exists():
        raise FileNotFoundError(f"Missing project template: {template_dir}")

    existing = find_project(root, project_name)
    if existing is not None:
        return existing

    values = _project_meta_values(project_name, stage=stage)
    project_dir = template_dir.parent / values["project_id"]
    if project_dir.exists():
        record = read_project_meta(project_dir)
        if record is None:
            raise RuntimeError(f"Cannot load project metadata from {project_dir}")
        return record

    shutil.copytree(template_dir, project_dir)
    for path in project_dir.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix.lower() not in {".md", ".yaml", ".yml", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        atomic_write_text(path, _replace_tokens(text, values))

    _ensure_project_directories(project_dir)
    record = read_project_meta(project_dir)
    if record is None:
        raise RuntimeError(f"Failed to create project metadata in {project_dir}")
    return record


def ensure_project(root: Path, project_name: str | None, allow_create: bool = True) -> ProjectRecord | None:
    record = find_project(root, project_name)
    if record is not None:
        return record
    if not project_name or not allow_create:
        return None
    return create_project(root, project_name)


def touch_project_updated_at(root: Path, project: ProjectRecord) -> ProjectRecord:
    meta_path = Path(project.path) / "project_meta.yaml"
    data = load_yaml_or_json(meta_path)
    if not data:
        return project
    data["updated_at"] = iso_now()
    lines = []
    for key in [
        "project_id",
        "project_name",
        "project_slug",
        "project_stage",
        "status",
        "created_at",
        "updated_at",
    ]:
        if key in data:
            value = data[key]
            if isinstance(value, str):
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f"{key}: {value}")
    atomic_write_text(meta_path, "\n".join(lines) + "\n")
    refreshed = read_project_meta(Path(project.path))
    return refreshed or project
