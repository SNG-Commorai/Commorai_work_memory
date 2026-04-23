# Inspiration: Consider adding to Commorai_work_memory...

- Created At: 2026-04-22T13:50:10+08:00
- Memory ID: 957ddb59-64c9-4344-ac32-53d9673f224b
- Type: short
- Field/Module:
- Importance: 3
- Confidence: 3
- Status: active
- Tags: idea, architecture_design
- Related Project: Commorai_work_memory

## Content
Consider adding a lightweight semantic retrieval layer to Commorai_work_memory:
1. Use a local embedding model such as BGE-M3-small to vectorize memory content.
2. Add semantic similarity ranking on top of the `search` command.
3. Keep the current file-system structure unchanged and only add a `.vector_index` file.
4. This preserves transparency and control while adding fuzzy matching capability.
