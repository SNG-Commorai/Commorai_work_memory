"""Shared helpers for the local memory runtime."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


MEMORY_TYPE_ALIASES = {
    "base": "base_memory",
    "base_memory": "base_memory",
    "project": "project_memory",
    "project_memory": "project_memory",
    "short": "short_term_memory",
    "short_term_memory": "short_term_memory",
}

SHORT_SUBTYPE_ALIASES = {
    "inspiration": "inspiration",
    "spark": "inspiration",
    "sparks": "inspiration",
    "research": "temporary_research",
    "temporary_research": "temporary_research",
    "analysis": "temporary_analysis",
    "temporary_analysis": "temporary_analysis",
    "task": "short_task",
    "tasks": "short_task",
    "todo": "short_task",
    "needs_review": "needs_review",
    "review": "needs_review",
    "to_review": "needs_review",
}

PROJECT_MODULE_ALIASES = {
    "research": "research",
    "analysis": "analysis",
    "tool": "tools",
    "tools": "tools",
    "decision": "decisions",
    "decisions": "decisions",
    "question": "questions",
    "questions": "questions",
    "reference": "references",
    "references": "references",
    "deliverable": "deliverables",
    "deliverables": "deliverables",
}

BASE_FIELDS = {
    "work_scope": "01_Base_Memory/work_scope.md",
    "work_style": "01_Base_Memory/work_style.md",
    "preferences": "01_Base_Memory/preferences.md",
    "analysis_methods": "01_Base_Memory/analysis_methods.md",
    "reusable_principles": "01_Base_Memory/reusable_principles.md",
    "glossary": "01_Base_Memory/glossary.md",
    "long_term_planning": "01_Base_Memory/long_term_planning.md",
}


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slugify(value: str, fallback: str = "item", max_length: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = slug[:max_length].strip("-")
    return slug or fallback


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def first_meaningful_line(content: str) -> str:
    for raw_line in (content or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        if line:
            return line
    return ""


def derive_summary(content: str, fallback: str = "Untitled memory") -> str:
    cleaned = compact_text(content)
    if not cleaned:
        return fallback
    if len(cleaned) <= 140:
        return cleaned
    return cleaned[:137].rstrip() + "..."


def derive_title(content: str, summary: str | None = None) -> str:
    line = first_meaningful_line(content)
    if not line:
        line = summary or derive_summary(content)
    words = line.split()
    if len(words) > 10:
        line = " ".join(words[:10])
    return line[:120].strip() or "Untitled Memory"


def coerce_int(value: Any, default: int = 3, minimum: int = 1, maximum: int = 5) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return min(max(number, minimum), maximum)


def normalize_memory_type(raw: str | None, default: str = "short_term_memory") -> str:
    return MEMORY_TYPE_ALIASES.get(compact_text(raw or "").lower(), default)


def normalize_short_subtype(raw: str | None) -> str | None:
    key = compact_text(raw or "").lower()
    if not key:
        return None
    return SHORT_SUBTYPE_ALIASES.get(key, slugify(key, fallback="needs-review").replace("-", "_"))


def normalize_project_module(raw: str | None) -> str | None:
    key = compact_text(raw or "").lower()
    if not key:
        return None
    return PROJECT_MODULE_ALIASES.get(key, slugify(key, fallback="general").replace("-", "_"))


def normalize_field(raw: str | None) -> str | None:
    key = compact_text(raw or "").lower().replace("-", "_")
    return key or None


def ensure_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = str(value).split(",")
    normalized: list[str] = []
    for item in items:
        cleaned = compact_text(str(item))
        if cleaned and cleaned not in normalized:
            normalized.append(cleaned)
    return normalized


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_scalar(value: str) -> Any:
    cleaned = value.strip()
    if cleaned == "":
        return ""
    if cleaned in {"true", "True"}:
        return True
    if cleaned in {"false", "False"}:
        return False
    if cleaned in {"null", "None"}:
        return None
    if cleaned == "[]":
        return []
    if cleaned == "{}":
        return {}
    if re.fullmatch(r"-?\d+", cleaned):
        return int(cleaned)
    if re.fullmatch(r"-?\d+\.\d+", cleaned):
        return float(cleaned)
    return strip_quotes(cleaned)


def _parse_block(lines: list[tuple[int, str]], start: int, indent: int) -> tuple[Any, int]:
    mapping: dict[str, Any] = {}
    array: list[Any] | None = None
    index = start
    while index < len(lines):
        current_indent, raw = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError(f"Unexpected indentation near: {raw}")
        if raw.startswith("- "):
            if array is None:
                array = []
            value = raw[2:].strip()
            if value:
                array.append(parse_scalar(value))
                index += 1
                continue
            nested, next_index = _parse_block(lines, index + 1, indent + 2)
            array.append(nested)
            index = next_index
            continue

        if array is not None:
            raise ValueError("Cannot mix list and mapping items at same indentation level.")

        key, _, remainder = raw.partition(":")
        key = key.strip()
        if not key:
            raise ValueError(f"Missing key near: {raw}")
        if remainder.strip():
            mapping[key] = parse_scalar(remainder.strip())
            index += 1
            continue
        if index + 1 < len(lines) and lines[index + 1][0] > indent:
            nested, next_index = _parse_block(lines, index + 1, indent + 2)
            mapping[key] = nested
            index = next_index
            continue
        mapping[key] = ""
        index += 1

    if array is not None:
        return array, index
    return mapping, index


def parse_simple_yaml(text: str) -> dict[str, Any]:
    prepared: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue
        stripped = raw_line.lstrip()
        if stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(stripped)
        prepared.append((indent, stripped))
    if not prepared:
        return {}
    parsed, _next_index = _parse_block(prepared, 0, prepared[0][0])
    if isinstance(parsed, dict):
        return parsed
    raise ValueError("Top-level YAML value must be a mapping.")


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return {}
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ImportError:
            return parse_simple_yaml(text)
        loaded = yaml.safe_load(text)  # type: ignore[attr-defined]
        return loaded or {}
    if isinstance(parsed, dict):
        return parsed
    raise ValueError(f"Expected mapping in config file: {path}")


def dump_pretty_json(data: Any) -> str:
    payload = asdict(data) if is_dataclass(data) else data
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def safe_relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
