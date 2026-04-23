# Agent Usage Manual

## Writing Principles

- Write to Base Memory only when the field is explicit.
- Write to Project Memory only when the project name is explicit.
- Default uncertain ownership to Short-Term Memory.
- Return a write summary after each operation.

## Base Memory Trigger

```yaml
memory_type: base_memory
field: work_style / preferences / analytical_method / long_term_plan
content: ...
```

## Project Memory Trigger

```yaml
memory_type: project_memory
project_name: ...
module: research / analysis / tools / decisions / questions / deliverables
content: ...
```

## Short-Term Memory Trigger

```yaml
memory_type: short_term_memory
subtype: inspiration / temporary_research / temporary_analysis / short_task / needs_review
content: ...
```

## Review Recommendations

- Review short-term memory regularly and migrate anything that remains useful.
- Run the sensitive information scan before pushing.
- Confirm that all examples are sanitized before sharing externally.
