# Commorai Work Memory

Commorai Work Memory is a local-first memory system framework for organizing long-term work memory, project-based memory, and short-term memory for AI-assisted workflows.

## Core Idea

The system organizes memory into three layers:

1. Base Memory  
   Stable long-term information such as working style, preferences, planning principles, recurring analytical methods, and durable workflow patterns.

2. Project Memory  
   Project-specific memory folders that store research, analysis, decisions, tools, references, and deliverables.

3. Short-Term Memory  
   Temporary ideas, quick research, spontaneous insights, short tasks, and items waiting to be reviewed or migrated.

## Architecture

- `00_System`: logs, indexes, rules, governance
- `01_Base_Memory`: stable long-term memory
- `02_Project_Memory`: project-based memory
- `03_Short_Term_Memory`: temporary and unsorted memory
- `04_Context_Builder`: context generation outputs
- `99_Archive`: archived or deprecated memory

## Privacy First

This repository is designed to be open-source, but real memory data should stay local.

Do not commit:

- personal memories
- work logs
- project-sensitive data
- private research
- generated context files
- API keys
- tokens
- `.env` files
- logs

## Quick Start

1. Clone the repository.
2. Run `python3 scripts/init_project.py`.
3. Use the prompt templates in `prompts/` to trigger memory writes.
4. Keep private memory files local and ignored by Git.

## Repository Layout

- `docs/`: framework and governance documentation
- `prompts/`: agent prompts and write triggers
- `schemas/`: JSON Schema files for memory objects and context requests
- `templates/`: reusable Markdown and YAML templates
- `examples/`: sanitized example content only
- `scripts/`: local-only maintenance scripts

## License

MIT License.
