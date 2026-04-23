# Memory Trigger Prompts

## Base Memory Example

```yaml
memory_type: base_memory
field: work_style
update_mode: append
importance: 4
confidence: 5
tags: [work_habits, output_preferences]
content: |
  I prefer seeing a structured framework before diving into the details.
```

## Project Memory Example

```yaml
memory_type: project_memory
project_name: Example_Project
module: research
update_mode: append
importance: 4
confidence: 4
tags: [market_research, case_analysis]
content: |
  This is a sanitized example of a project research note.
```

## Short-Term Memory Example

```yaml
memory_type: short_term_memory
subtype: inspiration
retention_days: 30
project_name: Example_Project
needs_migration: undecided
content: |
  This is a temporary inspiration example.
```
