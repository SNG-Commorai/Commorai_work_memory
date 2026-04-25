from __future__ import annotations

from pathlib import Path


CONFIG_YAML = """\
auto_trigger:
  enabled: true
  flush_point: end_of_turn
  capture_user: true
  capture_assistant: true
  capture_tool_results: true
  allow_auto_create_project: true
  base_memory_requires_explicit_or_repeated: true
  fallback_route: "short_term_memory:needs_review"
  dedupe_window_hours: 72
routing:
  base_memory:
    work_scope: 01_Base_Memory/work_scope.md
    work_style: 01_Base_Memory/work_style.md
    preferences: 01_Base_Memory/preferences.md
    analysis_methods: 01_Base_Memory/analysis_methods.md
    reusable_principles: 01_Base_Memory/reusable_principles.md
    glossary: 01_Base_Memory/glossary.md
    long_term_planning: 01_Base_Memory/long_term_planning.md
    conflicts: 01_Base_Memory/conflicts.md
  project_memory:
    research: research/notes
    analysis: analysis/outputs
    tools: tools/specs
    decisions: decisions.md
    questions: open_questions.md
    references: references
    deliverables: deliverables
    unknown_default: open_questions.md
    unknown_log_module: research
  short_term:
    inspiration: 03_Short_Term_Memory/sparks
    temporary_research: 03_Short_Term_Memory/temp_research
    temporary_analysis: 03_Short_Term_Memory/temp_analysis
    short_task: 03_Short_Term_Memory/tasks
    needs_review: 03_Short_Term_Memory/to_review
    default: 03_Short_Term_Memory/inbox.md
files:
  event_log: 00_System/logs/memory_events.jsonl
  operation_log: 00_System/logs/operation_log.md
  content_hashes: 00_System/indexes/content_hashes.json
  base_index: 01_Base_Memory/base_index.md
  short_index: 03_Short_Term_Memory/short_index.md
  project_index: 02_Project_Memory/project_index.md
  project_template: 02_Project_Memory/_Project_Template
"""


BASE_TEMPLATE = """\
# {title}

Records stable memory for `{field}`.

## Entries
<!-- MEMORY_CONTENT_START -->
No formal entries yet.
<!-- MEMORY_CONTENT_END -->
"""


CONFLICT_TEMPLATE = """\
# Conflicts And Pending Confirmation

Records base-memory information that conflicts, remains unconfirmed, or requires manual review.

## Entries
<!-- MEMORY_CONTENT_START -->
No pending items.
<!-- MEMORY_CONTENT_END -->
"""


MARKER_TEMPLATE = """\
# {title}

## Entries
<!-- MEMORY_CONTENT_START -->
{placeholder}
<!-- MEMORY_CONTENT_END -->
"""


PROJECT_META_TEMPLATE = """\
project_id: P_YYYYMMDD_project-slug
project_name: "{{project_name}}"
project_slug: project-slug
project_stage: "{{project_stage}}"
status: active
created_at: "{{created_at}}"
updated_at: "{{updated_at}}"
"""


def bootstrap_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "memory_system_config.yaml").write_text(CONFIG_YAML, encoding="utf-8")

    for relative in [
        "00_System/logs",
        "00_System/indexes",
        "01_Base_Memory",
        "02_Project_Memory/_Project_Template/research/notes",
        "02_Project_Memory/_Project_Template/analysis/outputs",
        "02_Project_Memory/_Project_Template/tools/specs",
        "02_Project_Memory/_Project_Template/data",
        "02_Project_Memory/_Project_Template/references",
        "02_Project_Memory/_Project_Template/deliverables",
        "02_Project_Memory/_Project_Template/archive",
        "03_Short_Term_Memory/sparks",
        "03_Short_Term_Memory/temp_research",
        "03_Short_Term_Memory/temp_analysis",
        "03_Short_Term_Memory/tasks",
        "03_Short_Term_Memory/to_review",
    ]:
        (root / relative).mkdir(parents=True, exist_ok=True)

    base_fields = {
        "work_scope": "Work Scope",
        "work_style": "Work Style",
        "preferences": "Preferences",
        "analysis_methods": "Analysis Methods",
        "reusable_principles": "Reusable Principles",
        "glossary": "Glossary",
        "long_term_planning": "Long Term Planning",
    }
    for field, title in base_fields.items():
        (root / "01_Base_Memory" / f"{field}.md").write_text(
            BASE_TEMPLATE.format(title=title, field=field),
            encoding="utf-8",
        )
    (root / "01_Base_Memory" / "conflicts.md").write_text(CONFLICT_TEMPLATE, encoding="utf-8")
    (root / "01_Base_Memory" / "base_index.md").write_text("# Base Memory Index\n", encoding="utf-8")

    (root / "03_Short_Term_Memory" / "inbox.md").write_text(
        MARKER_TEMPLATE.format(title="Short-Term Inbox", placeholder="No records yet."),
        encoding="utf-8",
    )
    (root / "03_Short_Term_Memory" / "short_index.md").write_text("# Short-Term Memory Index\n", encoding="utf-8")

    template_root = root / "02_Project_Memory" / "_Project_Template"
    (template_root / "project_meta.yaml").write_text(PROJECT_META_TEMPLATE, encoding="utf-8")
    (template_root / "project_brief.md").write_text(
        MARKER_TEMPLATE.format(title="Project Brief", placeholder="No formal entries yet."),
        encoding="utf-8",
    )
    (template_root / "memory_log.md").write_text(
        MARKER_TEMPLATE.format(title="Project Memory Log", placeholder="No records yet."),
        encoding="utf-8",
    )
    (template_root / "decisions.md").write_text(
        MARKER_TEMPLATE.format(title="Decision Log", placeholder="No formal entries yet."),
        encoding="utf-8",
    )
    (template_root / "open_questions.md").write_text(
        MARKER_TEMPLATE.format(title="Open Questions", placeholder="No pending items."),
        encoding="utf-8",
    )
    (template_root / "research" / "research_index.md").write_text("# Research Index\n", encoding="utf-8")
    (template_root / "analysis" / "analysis_index.md").write_text("# Analysis Index\n", encoding="utf-8")
    (template_root / "tools" / "tools_index.md").write_text("# Tools Index\n", encoding="utf-8")
    (root / "02_Project_Memory" / "project_index.md").write_text("# Project Index\n", encoding="utf-8")

    (root / "00_System" / "logs" / "memory_events.jsonl").write_text("", encoding="utf-8")
    (root / "00_System" / "logs" / "operation_log.md").write_text("# Operation Log\n\n## Logs\n", encoding="utf-8")
