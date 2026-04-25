#!/usr/bin/env python3
"""Initialize or repair the Commorai Work Memory project structure."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DIRS = [
    "docs",
    "prompts",
    "schemas",
    "templates",
    "examples",
    "examples/example_project_memory",
    "scripts",
    "00_System",
    "00_System/logs",
    "00_System/indexes",
    "00_System/rules",
    "01_Base_Memory",
    "02_Project_Memory",
    "02_Project_Memory/_Project_Template",
    "02_Project_Memory/_Project_Template/research",
    "02_Project_Memory/_Project_Template/research/notes",
    "02_Project_Memory/_Project_Template/analysis",
    "02_Project_Memory/_Project_Template/analysis/outputs",
    "02_Project_Memory/_Project_Template/tools",
    "02_Project_Memory/_Project_Template/tools/specs",
    "02_Project_Memory/_Project_Template/data",
    "02_Project_Memory/_Project_Template/references",
    "02_Project_Memory/_Project_Template/deliverables",
    "02_Project_Memory/_Project_Template/archive",
    "03_Short_Term_Memory",
    "03_Short_Term_Memory/sparks",
    "03_Short_Term_Memory/temp_research",
    "03_Short_Term_Memory/temp_analysis",
    "03_Short_Term_Memory/tasks",
    "03_Short_Term_Memory/to_review",
    "04_Context_Builder",
    "04_Context_Builder/generated_contexts",
    "99_Archive",
]

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".gitignore",
    ".gitattributes",
    "project_manifest.yaml",
    "memory_system_config.yaml",
    "docs/framework_overview.md",
    "docs/memory_architecture.md",
    "docs/memory_processing_rules.md",
    "docs/agent_usage_manual.md",
    "docs/github_open_source_notes.md",
    "docs/privacy_and_safety_rules.md",
    "prompts/agent_master_prompt.md",
    "prompts/memory_trigger_prompts.md",
    "prompts/base_memory_prompts.md",
    "prompts/project_memory_prompts.md",
    "prompts/short_term_memory_prompts.md",
    "prompts/retrieval_prompts.md",
    "prompts/review_and_migration_prompts.md",
    "schemas/memory_event.schema.json",
    "schemas/base_memory.schema.json",
    "schemas/project_memory.schema.json",
    "schemas/short_term_memory.schema.json",
    "schemas/context_request.schema.json",
    "templates/base_memory_template.md",
    "templates/project_meta_template.yaml",
    "templates/project_brief_template.md",
    "templates/project_memory_log_template.md",
    "templates/short_term_memory_template.md",
    "templates/decision_log_template.md",
    "templates/open_questions_template.md",
    "templates/context_output_template.md",
    "examples/example_base_memory.md",
    "examples/example_short_term_memory.md",
    "examples/example_project_memory/project_meta.yaml",
    "examples/example_project_memory/project_brief.md",
    "examples/example_project_memory/memory_log.md",
    "examples/example_project_memory/decisions.md",
    "examples/example_project_memory/open_questions.md",
    "00_System/README.md",
    "00_System/rules/writing_rules.md",
    "00_System/rules/retrieval_rules.md",
    "00_System/rules/governance_rules.md",
    "01_Base_Memory/README.md",
    "02_Project_Memory/README.md",
    "03_Short_Term_Memory/README.md",
    "04_Context_Builder/README.md",
    "99_Archive/README.md",
    "00_System/logs/.gitkeep",
    "00_System/indexes/.gitkeep",
    "01_Base_Memory/.gitkeep",
    "02_Project_Memory/.gitkeep",
    "03_Short_Term_Memory/.gitkeep",
    "04_Context_Builder/.gitkeep",
    "04_Context_Builder/generated_contexts/.gitkeep",
    "99_Archive/.gitkeep",
    "01_Base_Memory/work_scope.md",
    "01_Base_Memory/work_style.md",
    "01_Base_Memory/preferences.md",
    "01_Base_Memory/analysis_methods.md",
    "01_Base_Memory/reusable_principles.md",
    "01_Base_Memory/glossary.md",
    "01_Base_Memory/long_term_planning.md",
    "01_Base_Memory/conflicts.md",
    "01_Base_Memory/base_index.md",
    "02_Project_Memory/project_index.md",
    "02_Project_Memory/_Project_Template/project_meta.yaml",
    "02_Project_Memory/_Project_Template/project_brief.md",
    "02_Project_Memory/_Project_Template/memory_log.md",
    "02_Project_Memory/_Project_Template/decisions.md",
    "02_Project_Memory/_Project_Template/open_questions.md",
    "02_Project_Memory/_Project_Template/research/research_index.md",
    "02_Project_Memory/_Project_Template/analysis/analysis_index.md",
    "02_Project_Memory/_Project_Template/tools/tools_index.md",
    "03_Short_Term_Memory/inbox.md",
    "03_Short_Term_Memory/short_index.md",
]


def placeholder_for(relative_path: str) -> str:
    path = Path(relative_path)
    name = path.name

    if relative_path.startswith("01_Base_Memory/") and name.endswith(".md") and name not in {"README.md", "base_index.md"}:
        title = path.stem.replace("_", " ").title()
        placeholder = "No pending items." if name == "conflicts.md" else "No formal entries yet."
        return (
            f"# {title}\n\n"
            "## Entries\n"
            "<!-- MEMORY_CONTENT_START -->\n"
            f"{placeholder}\n"
            "<!-- MEMORY_CONTENT_END -->\n"
        )
    if relative_path == "01_Base_Memory/base_index.md":
        return "# Base Memory Index\n"
    if relative_path == "02_Project_Memory/project_index.md":
        return "# Project Index\n"
    if relative_path == "03_Short_Term_Memory/inbox.md":
        return (
            "# Short-Term Inbox\n\n"
            "## Entries\n"
            "<!-- MEMORY_CONTENT_START -->\n"
            "No records yet.\n"
            "<!-- MEMORY_CONTENT_END -->\n"
        )
    if relative_path == "03_Short_Term_Memory/short_index.md":
        return "# Short-Term Memory Index\n"
    if relative_path == "02_Project_Memory/_Project_Template/project_meta.yaml":
        return (
            "project_id: P_YYYYMMDD_project-slug\n"
            'project_name: "{{project_name}}"\n'
            "project_slug: project-slug\n"
            'project_stage: "{{project_stage}}"\n'
            "status: active\n"
            'created_at: "{{created_at}}"\n'
            'updated_at: "{{updated_at}}"\n'
        )
    if relative_path in {
        "02_Project_Memory/_Project_Template/project_brief.md",
        "02_Project_Memory/_Project_Template/memory_log.md",
        "02_Project_Memory/_Project_Template/decisions.md",
        "02_Project_Memory/_Project_Template/open_questions.md",
    }:
        title_map = {
            "project_brief.md": ("Project Brief", "No formal entries yet."),
            "memory_log.md": ("Project Memory Log", "No records yet."),
            "decisions.md": ("Project Decisions", "No formal entries yet."),
            "open_questions.md": ("Open Questions", "No pending items."),
        }
        title, placeholder = title_map[name]
        return (
            f"# {title}\n\n"
            "## Entries\n"
            "<!-- MEMORY_CONTENT_START -->\n"
            f"{placeholder}\n"
            "<!-- MEMORY_CONTENT_END -->\n"
        )
    if relative_path.endswith("research/research_index.md"):
        return "# Research Index\n"
    if relative_path.endswith("analysis/analysis_index.md"):
        return "# Analysis Index\n"
    if relative_path.endswith("tools/tools_index.md"):
        return "# Tools Index\n"
    if name == ".gitkeep":
        return ""
    if path.suffix == ".json":
        return "{}\n"
    if path.suffix in {".yaml", ".yml"}:
        return "# Placeholder generated by init_project.py\n"
    if name == "README.md" and path.parent == Path("."):
        return (
            "# Commorai Work Memory\n\n"
            "Placeholder README generated by init_project.py.\n"
        )
    title = path.stem.replace("_", " ").replace("-", " ").title()
    return f"# {title}\n\nPlaceholder generated by init_project.py.\n"


def ensure_project(root: Path) -> tuple[list[Path], list[Path]]:
    created_dirs: list[Path] = []
    created_files: list[Path] = []

    for rel_dir in REQUIRED_DIRS:
        target = root / rel_dir
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created_dirs.append(target)

    for rel_file in REQUIRED_FILES:
        target = root / rel_file
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(placeholder_for(rel_file), encoding="utf-8")
            created_files.append(target)

    return created_dirs, created_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize missing directories and placeholder files."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root to initialize. Defaults to the current repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    created_dirs, created_files = ensure_project(root)

    print("Initialization summary")
    print(f"- root: {root}")
    print(f"- directories created: {len(created_dirs)}")
    print(f"- files created: {len(created_files)}")

    if created_dirs:
        print("- new directories:")
        for item in created_dirs:
            print(f"  {item.relative_to(root)}")

    if created_files:
        print("- new files:")
        for item in created_files:
            print(f"  {item.relative_to(root)}")

    if not created_dirs and not created_files:
        print("- no changes needed")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
