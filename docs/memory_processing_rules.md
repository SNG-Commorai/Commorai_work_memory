# Memory Processing Rules

1. Receive the input
2. Parse field hints
3. Generate a `memory_event`
4. Determine the memory type
5. Write to the appropriate location
6. Update indexes
7. Check for conflicts
8. Return a write summary

## Governance Notes

- Do not promote content to Base Memory unless the user explicitly provides a long-term field.
- If the user does not explicitly provide a project name, default to Short-Term Memory.
- If potentially sensitive content is detected, sanitize it first or stop the write.
- Record conflicts instead of overwriting content directly.
