# Project Memory Prompts

Templates for triggering project memory writes.
Write to Project Memory only when the user provides a project name or clearly states that the information belongs to a specific project.
If the project does not exist, create the project folder automatically.
Project modules include research, analysis, tools, decisions, questions, references, and deliverables.

Example:

```yaml
memory_type: project_memory
project_name: Example_Project
module: decisions
content: |
  This project should prioritize local file storage and avoid introducing an external database.
```
