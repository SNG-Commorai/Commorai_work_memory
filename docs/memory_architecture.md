# Memory Architecture

## Runtime Boundary

This repository's automation boundary is local end-of-turn processing, not a hosted chat integration. `memory.py capture-turn` and `memory_core.engine.process_turn(...)` are the reusable auto-trigger entrypoints.

## Canonical Event Model

All new writes use one canonical `memory_event` record with:

- `memory_id`
- `created_at`
- `updated_at`
- `memory_type`
- `title`
- `summary`
- `content`
- `project_name`
- `project_id`
- `field`
- `module`
- `subtype`
- `field_or_module`
- `tags`
- `importance`
- `confidence`
- `source`
- `privacy_level`
- `status`
- `update_mode`
- `target_path`
- `links`
- `session_id`
- `turn_id`
- `source_event_id`
- `content_hash`

The canonical JSONL log lives at `00_System/logs/memory_events.jsonl`.

## Core Modules

`memory_core/models.py`

- dataclasses for candidates, turn contexts, canonical events, project records, and write results

`memory_core/extractor.py`

- conservative rule-based extraction for `capture-turn`
- structured candidates win over inferred ones

`memory_core/router.py`

- deterministic routing into base, project, or short-term memory
- resolves final field/module/subtype and target path

`memory_core/writers.py`

- writes standalone entry files
- writes marker-based files safely inside template blocks
- updates per-project logs

`memory_core/indexers.py`

- rebuilds base, project, module, and short-term indexes from canonical metadata

`memory_core/dedupe.py`

- computes stable hashes
- tracks dedupe state in `00_System/indexes/content_hashes.json`
- checks conservative base-memory conflicts

`memory_core/project_registry.py`

- resolves projects by exact name, slug, or project id
- creates new project spaces from `02_Project_Memory/_Project_Template`

`memory_core/marker_io.py`

- atomic write helpers
- best-effort file locking
- safe marker insertion

`memory_core/engine.py`

- orchestrates extract -> normalize -> dedupe -> persist -> index -> log
- exposes `add_manual_memory`, `process_turn`, `rebuild_indexes`, `review_short`, and `migrate_legacy`

## Persistence Model

Base memory:

- fixed field-to-file mapping under `01_Base_Memory/`
- conflicts are redirected to `01_Base_Memory/conflicts.md`

Project memory:

- template-backed project directories under `02_Project_Memory/`
- standalone research/analysis/tools/reference/deliverable entries
- marker-updated `decisions.md` and `open_questions.md`

Short-term memory:

- file-per-entry buckets for sparks, temp research, temp analysis, tasks, and review
- marker-backed `inbox.md` fallback

## Rebuildability

The runtime is designed so that:

- content files remain readable as Markdown
- all writes are auditable through canonical JSONL metadata
- indexes can be rebuilt from metadata without contacting any external service
