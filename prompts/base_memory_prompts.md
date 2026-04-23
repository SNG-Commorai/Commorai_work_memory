# Base Memory Prompts

Templates for triggering base memory writes.
Write to Base Memory only when the user explicitly says "base memory" or provides a field hint.
Supported fields include work content, work style, long-term planning, preferences, analytical methods, reuse principles, glossary entries, and boundary conditions.

Example:

```yaml
memory_type: base_memory
field: analytical_method
content: |
  When doing comparative analysis, define the evaluation dimensions first and then assess the strength of evidence for each option.
```
