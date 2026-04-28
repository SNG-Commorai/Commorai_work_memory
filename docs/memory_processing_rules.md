# Memory Processing Rules

The runtime follows one deterministic write pipeline for both manual writes and end-of-turn capture:

1. Receive a manual memory request or a turn context.
2. Normalize the request into a canonical candidate.
3. If the input is a turn capture, extract conservative candidates from structured candidates first, then from local text rules.
4. Route the candidate into `base_memory`, `project_memory`, or `short_term_memory`.
5. Resolve the final field/module/subtype and the final `target_path`.
6. Compute `content_hash` and skip exact duplicates.
7. For base-memory collisions on the same title slug, record a conflict instead of overwriting.
8. Persist content using marker-safe insertion or standalone entry files.
9. Append a canonical JSONL record to `00_System/logs/memory_events.jsonl`.
10. Refresh indexes and the content-hash registry.

## Base Memory Rules

- Base memory is intentionally strict.
- Valid fields are:
  - `work_scope`
  - `work_style`
  - `preferences`
  - `analysis_methods`
  - `reusable_principles`
  - `glossary`
  - `long_term_planning`
- If a write is not explicit enough for base memory, it must be downgraded to short-term review instead of being promoted automatically.

## Project Memory Rules

- Project memory is allowed when a project name is explicit, an active project exists in `capture-turn`, or a project can be resolved from the registry.
- `research`, `analysis`, `tools`, `references`, and `deliverables` create standalone Markdown entries.
- `decisions` and `questions` update marker-based files.
- Every project write also appends a summary line to `memory_log.md`.

## Short-Term Memory Rules

- Legacy `--module inspiration` calls with `--memory-type short` are normalized to `subtype=inspiration`.
- Unknown short-term subtypes do not fail the write; they fall back to `inbox.md`.
- `needs_review` is the default destination for ambiguous `capture-turn` content.

## Marker Write Rules

- If a file contains `<!-- MEMORY_CONTENT_START -->` and `<!-- MEMORY_CONTENT_END -->`, new content must be inserted between them.
- Placeholder text such as `No records yet.` or `No pending items.` must be replaced on the first write.
- If markers are absent, the runtime may fall back to append-style atomic writes.

## Dedupe And Conflict Rules

- Exact duplicates are detected with:
  - normalized content
  - memory type
  - project name
  - field
  - module
  - subtype
- Duplicate writes are logged with:
  - `status=duplicate_skipped`
  - `update_mode=noop`
- Base-memory conflicts are logged with:
  - `status=conflict_recorded`
  - `update_mode=conflict_only`

## Retrieval Rules

- `build-context` first recalls candidates from canonical logs and indexes.
- It then reopens the matched files and extracts excerpts from their content.
- If metadata recall is insufficient, it falls back to local file scanning.
