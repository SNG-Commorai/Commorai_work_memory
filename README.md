# Commorai Work Memory

Commorai Work Memory is a local-first memory framework for AI-assisted work. It helps individuals and teams organize durable knowledge, project context, and short-term notes in a way that can be reused across sessions, tools, and workflows.

Commorai Work Memory 是一个面向 AI 辅助工作的本地优先记忆框架。它帮助个人和团队组织长期知识、项目上下文和短期记录，并让这些内容能够在不同会话、工具和工作流程之间复用。

Instead of treating every AI interaction as an isolated prompt, the framework provides a structured layer for preserving research, decisions, references, and outputs while keeping sensitive memory data local.

它不把每一次 AI 交互都视为孤立提示，而是提供一个结构化记忆层，用于保存研究过程、决策记录、参考资料和工作产出，同时让敏感记忆数据保留在本地。

---

## Core Concept / 核心理念

The framework organizes memory into three complementary layers:

该框架将记忆划分为三个相互补充的层次：

### 1. Base Memory / 基础记忆

Stable long-term information such as working style, preferences, planning principles, recurring analytical methods, and durable workflow patterns.

用于存放稳定的长期信息，例如工作风格、个人偏好、规划原则、可复用的分析方法，以及长期有效的工作流程模式。

### 2. Project Memory / 项目记忆

Project-specific memory spaces for storing research, analysis, decisions, tools, references, and deliverables.

以项目为单位建立记忆空间，用于保存研究资料、分析结果、决策记录、工具、参考资料和交付成果。

### 3. Short-Term Memory / 短期记忆

Temporary ideas, quick research notes, spontaneous insights, short tasks, and items waiting to be reviewed, organized, or migrated.

用于存放临时想法、快速研究记录、即时洞察、短任务，以及等待整理、归类或迁移的内容。

---

## Key Features / 核心特性

- Layered memory model for separating durable knowledge, project context, and temporary notes  
  分层记忆模型，用于区分长期知识、项目上下文与临时记录

- Local-first structure for keeping sensitive data under your control by default  
  本地优先结构，默认让敏感数据始终由你掌控

- Reusable prompts, templates, and schemas for consistent memory capture  
  可复用的提示模板、文档模板与 Schema，帮助你稳定记录记忆

- Project-oriented organization for preserving research, decisions, and deliverables in one place  
  项目导向的组织方式，让研究、决策和交付物保存在同一上下文中

- Context builder outputs for assembling reusable AI context across sessions  
  上下文构建输出，用于在不同会话之间复用 AI 工作上下文

- Archive-friendly structure for retiring outdated memory without losing useful history  
  便于归档的结构设计，帮助你在不丢失历史价值的前提下整理旧内容

---

## Repository Structure / 仓库结构

- `00_System` — logs, indexes, rules, and governance / 日志、索引、规则与治理
- `01_Base_Memory` — stable long-term memory / 稳定的长期记忆
- `02_Project_Memory` — project-based memory / 项目型记忆
- `03_Short_Term_Memory` — temporary and unsorted memory / 临时与未整理记忆
- `04_Context_Builder` — generated context outputs / 上下文构建输出
- `99_Archive` — archived or deprecated memory / 归档或已弃用记忆

---

## Typical Workflow / 典型工作流

1. Capture new information in `03_Short_Term_Memory`. / 先将新信息记录到 `03_Short_Term_Memory`。  
2. Review and move durable content into `01_Base_Memory` or `02_Project_Memory`. / 定期整理，并将长期有效内容迁移到 `01_Base_Memory` 或 `02_Project_Memory`。  
3. Use prompts and templates to build reusable context. / 使用提示词与模板生成可复用上下文。  
4. Keep decisions, references, and deliverables close to the work itself. / 将决策、参考资料和交付成果保存在与实际工作最接近的位置。  
5. Archive outdated memory without deleting useful history. / 对过时内容进行归档，同时保留有价值的历史记录。  

---

## Quick Start / 快速开始

1. Clone the repository. / 克隆仓库。  
2. Run the initialization script. / 运行初始化脚本。  

```bash
python3 scripts/init_project.py
```

3. Review the templates in `templates/` and the prompts in `prompts/`. / 查看 `templates/` 中的模板和 `prompts/` 中的提示词。  
4. Start capturing notes into `03_Short_Term_Memory`. / 从 `03_Short_Term_Memory` 开始记录笔记与临时想法。  
5. Move durable knowledge into `01_Base_Memory` and project-specific material into `02_Project_Memory`. / 将长期有效的内容迁移到 `01_Base_Memory`，将项目相关内容迁移到 `02_Project_Memory`。  

---

## Privacy First / 隐私优先

This repository is intended to be open-source, but real memory data should remain local.

本仓库适合作为开源框架使用，但真实记忆数据应始终保留在本地。

**Do not commit:**  
**请不要提交：**

- personal memories / 个人记忆
- work logs / 工作日志
- project-sensitive data / 项目敏感数据
- private research / 私人研究资料
- generated context files / 生成的上下文文件
- API keys / API 密钥
- tokens / 访问令牌
- `.env` files / `.env` 文件
- logs / 日志文件

---

## Suggested Git Hygiene / 建议的 Git 管理方式

Store real memory locally and ignore sensitive files in Git so the framework can stay open while the data remains private.

建议将真实记忆保存在本地，并通过 Git 忽略敏感文件，从而实现“框架开放、数据私有”。

```gitignore
# Private memory data
03_Short_Term_Memory/**
04_Context_Builder/**
00_System/logs/**

# Secrets
.env
*.key
*.token

# Local outputs
*.log
*.tmp
```

You may keep only sanitized examples in the repository and store real working memory in an ignored local directory.

你也可以只在仓库中保留脱敏示例，而把真实工作记忆放在被忽略的本地目录中。

---

## Roadmap / 路线图

- richer prompt libraries / 更丰富的提示模板库
- stronger schemas for memory objects / 更完善的记忆对象 Schema
- better context builder workflows / 更成熟的上下文构建流程
- migration and archival utilities / 迁移与归档工具
- integrations with local AI tooling / 与本地 AI 工具的集成能力

---

## Contributing / 贡献方式

Contributions are welcome, especially around documentation, templates, schemas, workflow examples, and local tooling. Please do not submit any real personal memory or sensitive project material.

欢迎围绕文档、模板、Schema、工作流示例和本地工具进行贡献。请不要提交任何真实个人记忆或敏感项目材料。

---

## License / 许可证

Released under the MIT License.  
基于 MIT License 开源。
