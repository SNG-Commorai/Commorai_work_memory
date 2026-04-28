"""Configuration loading for the local memory runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .utils import load_yaml_or_json


DEFAULT_CONFIG: dict[str, Any] = {
    "auto_trigger": {
        "enabled": True,
        "flush_point": "end_of_turn",
        "capture_user": True,
        "capture_assistant": True,
        "capture_tool_results": True,
        "allow_auto_create_project": True,
        "base_memory_requires_explicit_or_repeated": True,
        "fallback_route": "short_term_memory:needs_review",
        "dedupe_window_hours": 72,
    },
    "routing": {
        "base_memory": {
            "work_scope": "01_Base_Memory/work_scope.md",
            "work_style": "01_Base_Memory/work_style.md",
            "preferences": "01_Base_Memory/preferences.md",
            "analysis_methods": "01_Base_Memory/analysis_methods.md",
            "reusable_principles": "01_Base_Memory/reusable_principles.md",
            "glossary": "01_Base_Memory/glossary.md",
            "long_term_planning": "01_Base_Memory/long_term_planning.md",
            "conflicts": "01_Base_Memory/conflicts.md",
        },
        "project_memory": {
            "research": "research/notes",
            "analysis": "analysis/outputs",
            "tools": "tools/specs",
            "decisions": "decisions.md",
            "questions": "open_questions.md",
            "references": "references",
            "deliverables": "deliverables",
            "unknown_default": "open_questions.md",
            "unknown_log_module": "research",
        },
        "short_term": {
            "inspiration": "03_Short_Term_Memory/sparks",
            "temporary_research": "03_Short_Term_Memory/temp_research",
            "temporary_analysis": "03_Short_Term_Memory/temp_analysis",
            "short_task": "03_Short_Term_Memory/tasks",
            "needs_review": "03_Short_Term_Memory/to_review",
            "default": "03_Short_Term_Memory/inbox.md",
        },
    },
    "files": {
        "event_log": "00_System/logs/memory_events.jsonl",
        "operation_log": "00_System/logs/operation_log.md",
        "content_hashes": "00_System/indexes/content_hashes.json",
        "base_index": "01_Base_Memory/base_index.md",
        "short_index": "03_Short_Term_Memory/short_index.md",
        "project_index": "02_Project_Memory/project_index.md",
        "project_template": "02_Project_Memory/_Project_Template",
    },
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(root: Path) -> dict[str, Any]:
    config_path = root / "memory_system_config.yaml"
    loaded = load_yaml_or_json(config_path)
    return deep_merge(DEFAULT_CONFIG, loaded)
