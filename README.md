# Commorai Work Memory

Commorai Work Memory is a local-first memory runtime for AI-assisted work. It helps individuals and teams organize durable knowledge, project context, and short-term working memory in transparent Markdown and JSONL files that can be reused across sessions, tools, and workflows.

Commorai Work Memory 是一个面向 AI 辅助工作的本地优先记忆运行时。它帮助个人和团队将长期知识、项目上下文和短期工作记忆组织为透明的 Markdown 与 JSONL 文件，并让这些内容能够在不同会话、工具和工作流程之间复用。

Instead of treating every AI interaction as an isolated prompt, the framework provides a structured runtime for capturing, routing, deduplicating, indexing, and rebuilding memory while keeping sensitive memory data local.

它不把每一次 AI 交互都视为孤立提示，而是提供一个结构化运行层，用于捕获、路由、去重、索引和重建记忆，同时让敏感记忆数据保留在本地。

---

## Core Concept / 核心理念

The framework organizes memory into three complementary layers:

该框架将记忆划分为三个相互补充的层次：

### 1. Base Memory / 基础记忆

Stable long-term information such as working style, preferences, planning principles, recurring analytical methods, reusable workflow patterns, glossary terms, and durable scope definitions.

用于存放稳定的长期信息，例如工作风格、个人偏好、规划原则、可复用的分析方法、长期有效的工作流程模式、术语表和工作范围定义。

Base Memory is intentionally conservative. Automatic turn capture does not freely write ordinary conversation into Base Memory; durable base information should be explicit, structured, or repeatedly confirmed.

基础记忆会被谨慎处理。自动回合捕获不会随意将普通对话写入基础记忆；长期有效的基础信息应当是明确、结构化或被反复确认的。

### 2. Project Memory / 项目记忆

Project-specific memory spaces for storing research, analysis, decisions, tools, references, open questions, and deliverables.

以项目为单位建立记忆空间，用于保存研究资料、分析结果、决策记录、工具说明、参考资料、开放问题和交付成果。

When an active project is provided, turn-level memory can be routed into the corresponding project space and reflected in project indexes and module indexes.

当提供当前项目名时，回合级记忆可以被路由到对应的项目空间，并同步反映到项目索引和模块索引中。

### 3. Short-Term Memory / 短期记忆

Temporary ideas, quick research notes, spontaneous insights, short tasks, temporary analysis, and items waiting to be reviewed, organized, or migrated.

用于存放临时想法、快速研究记录、即时洞察、短任务、临时分析，以及等待整理、归类或迁移的内容。

Ambiguous or low-confidence memory can safely fall back to Short-Term Memory instead of being forced into long-term or project memory.

不明确或置信度较低的记忆可以安全地回落到短期记忆，而不是被强行写入长期记忆或项目记忆。

---

## Key Features / 核心特性

- Layered memory model for separating durable knowledge, project context, and temporary notes  
  分层记忆模型，用于区分长期知识、项目上下文与临时记录

- Local-first runtime with transparent Markdown and JSONL storage  
  本地优先运行时，使用透明的 Markdown 与 JSONL 文件进行存储

- Unified CLI entrypoint through `memory.py`  
  通过 `memory.py` 提供统一的命令行入口

- Automatic routing into base, project, or short-term memory  
  自动路由到基础记忆、项目记忆或短期记忆

- End-of-turn capture entrypoint for agent workflows  
  面向 agent 工作流的回合结束捕获入口

- Deterministic pipeline for extraction, routing, dedupe, persistence, conflict handling, logging, and index rebuilding  
  用于提取、路由、去重、持久化、冲突处理、日志记录和索引重建的确定性流程

- Marker-safe writing into managed Markdown sections  
  基于标记区块的安全写入，避免破坏模板结构

- Context builder outputs for assembling reusable AI context across sessions  
  上下文构建输出，用于在不同会话之间复用 AI 工作上下文

- Privacy-first structure for keeping real working memory under local control  
  隐私优先结构，让真实工作记忆默认保留在本地控制之下

---

## Repository Structure / 仓库结构

- `memory.py` — unified local CLI runtime / 统一的本地命令行运行时
- `memory_core/` — models, routing, extraction, writers, dedupe, indexes, and project registry / 模型、路由、提取、写入、去重、索引与项目注册表
- `00_System` — logs, indexes, rules, and governance / 日志、索引、规则与治理
- `01_Base_Memory` — stable long-term memory / 稳定的长期记忆
- `02_Project_Memory` — project-based memory spaces / 项目型记忆空间
- `03_Short_Term_Memory` — temporary, reviewable, and unsorted memory / 临时、待审查与未整理记忆
- `04_Context_Builder` — generated context outputs / 上下文构建输出
- `docs` — architecture, usage, processing, and safety notes / 架构、使用、处理规则与安全说明
- `schemas` — JSON schemas for memory objects and events / 记忆对象与事件的 JSON Schema
- `templates` — reusable memory and project templates / 可复用记忆与项目模板
- `prompts` — prompt references for memory workflows / 记忆工作流提示词参考
- `tests` — local runtime tests / 本地运行时测试
- `99_Archive` — archived or deprecated memory / 归档或已弃用记忆

---

## Runtime Commands / 运行命令

The current version uses `memory.py` as the primary interface.

当前版本以 `memory.py` 作为主要使用入口。

### Initialize or repair the structure / 初始化或修复结构

```bash
python3 memory.py init
```

### Create or resolve a project / 创建或解析项目

```bash
python3 memory.py add-project "Commorai Work Memory"
```

### Add short-term memory / 写入短期记忆

```bash
python3 memory.py add \
  --memory-type short \
  --module inspiration \
  --content "A quick idea to review later"
```

### Add project memory / 写入项目记忆

```bash
python3 memory.py add \
  --memory-type project \
  --project-name "Commorai Work Memory" \
  --module research \
  --content "A project research note"
```

### Add base memory / 写入基础记忆

```bash
python3 memory.py add \
  --memory-type base \
  --field preferences \
  --content "Prefer structured output before long explanations"
```

### Capture one agent turn / 捕获一轮 agent 任务

```bash
python3 memory.py capture-turn \
  --session-id s1 \
  --turn-id t1 \
  --active-project "Commorai Work Memory" \
  --user-text "Please summarize the project findings" \
  --assistant-text "I summarized the findings and classified them into project memory"
```

### Capture one turn from JSON / 从 JSON 捕获一轮任务

```bash
python3 memory.py capture-turn --input turn.json
```

Example `turn.json`:

示例 `turn.json`：

```json
{
  "session_id": "s1",
  "turn_id": "t1",
  "active_project": "Commorai Work Memory",
  "user_text": "User request for this turn",
  "assistant_text": "Assistant response for this turn",
  "tool_outputs": [
    "Short tool result summary"
  ]
}
```

### Rebuild indexes / 重建索引

```bash
python3 memory.py rebuild-indexes
```

### Review short-term memory / 审查短期记忆

```bash
python3 memory.py review-short
```

### Build reusable context / 构建可复用上下文

```bash
python3 memory.py build-context \
  --task "Prepare next planning session" \
  --project-name "Commorai Work Memory" \
  --keyword "research" \
  --limit 5
```

### Scan sensitive files / 扫描敏感内容

```bash
python3 memory.py scan-sensitive
```

---

## Automatic Capture / 自动化捕获

The project includes an end-of-turn capture entrypoint through `memory.py capture-turn`.

该项目已经通过 `memory.py capture-turn` 提供了回合结束捕获入口。

This means an external agent, local assistant, IDE workflow, shell wrapper, or browser automation can call the CLI after each task and let the runtime classify and persist the turn.

这意味着外部 agent、本地助手、IDE 工作流、Shell 包装脚本或浏览器自动化流程，可以在每次任务结束后调用该命令，让运行时完成归类和持久化。

The runtime itself is local and generic. It is not tied to a specific chat product, hosted service, or external LLM API.

运行时本身是本地且通用的。它并不绑定特定聊天产品、托管服务或外部 LLM API。

A recommended agent flush pattern is:

推荐的 agent 写入模式是：

1. Keep the active project name when the task clearly belongs to a project. / 当任务明确属于某个项目时，保留当前项目名。  
2. Send user text, assistant text, and summarized tool outputs to `capture-turn`. / 将用户输入、助手输出和工具结果摘要发送给 `capture-turn`。  
3. Let ambiguous content fall back to Short-Term Memory. / 让不明确的内容回落到短期记忆。  
4. Write Base Memory only when the information is explicit, durable, or repeatedly confirmed. / 只有当信息明确、长期有效或被反复确认时，才写入基础记忆。  
5. Rebuild or review indexes when needed. / 在需要时重建或审查索引。  

---

## Routing Rules / 路由规则

### Base Memory / 基础记忆

Base Memory writes require a valid field such as `preferences`, `work_style`, `analysis_methods`, `reusable_principles`, `glossary`, `work_scope`, or `long_term_planning`.

基础记忆写入需要有效字段，例如 `preferences`、`work_style`、`analysis_methods`、`reusable_principles`、`glossary`、`work_scope` 或 `long_term_planning`。

Conflicting base-memory writes are recorded in `01_Base_Memory/conflicts.md` instead of silently overwriting existing content.

发生冲突的基础记忆写入会被记录到 `01_Base_Memory/conflicts.md`，而不是静默覆盖既有内容。

### Project Memory / 项目记忆

Project Memory is selected when a project name is explicit or when an active project is provided during `capture-turn`.

当显式提供项目名，或在 `capture-turn` 中提供当前项目时，内容会进入项目记忆。

Supported modules include `research`, `analysis`, `tools`, `references`, `deliverables`, `decisions`, and `questions`.

支持的模块包括 `research`、`analysis`、`tools`、`references`、`deliverables`、`decisions` 和 `questions`。

Standalone project notes are written as Markdown files, while managed files such as `decisions.md` and `open_questions.md` are updated through marker-safe insertion.

独立项目记录会被写为 Markdown 文件，而 `decisions.md` 和 `open_questions.md` 等受管理文件会通过标记区块安全插入内容。

### Short-Term Memory / 短期记忆

Short-Term Memory supports sparks, temporary research, temporary analysis, tasks, review queues, and a general inbox.

短期记忆支持灵感、临时研究、临时分析、任务、待审查队列和通用收件箱。

Unknown or ambiguous short-term writes fall back to `03_Short_Term_Memory/inbox.md`.

未知或不明确的短期写入会回落到 `03_Short_Term_Memory/inbox.md`。

---

## Dedupe, Logs, and Indexes / 去重、日志与索引

Every canonical memory event receives a stable content hash.

每个标准化记忆事件都会获得稳定的内容哈希。

Content hashes are tracked in `00_System/indexes/content_hashes.json`, and exact duplicates are skipped instead of being written repeatedly.

内容哈希会记录在 `00_System/indexes/content_hashes.json` 中，完全重复的内容会被跳过，而不是反复写入。

Memory activity is recorded in `00_System/logs/memory_events.jsonl`.

记忆活动会记录在 `00_System/logs/memory_events.jsonl` 中。

Indexes can be rebuilt with `python3 memory.py rebuild-indexes`.

索引可以通过 `python3 memory.py rebuild-indexes` 重建。

---

## Typical Workflow / 典型工作流

1. Initialize or repair the repository with `python3 memory.py init`. / 使用 `python3 memory.py init` 初始化或修复仓库结构。  
2. Capture new notes manually with `memory.py add`, or automatically with `memory.py capture-turn`. / 使用 `memory.py add` 手动记录新内容，或使用 `memory.py capture-turn` 自动捕获回合内容。  
3. Route project-specific material into `02_Project_Memory`. / 将项目相关内容路由到 `02_Project_Memory`。  
4. Keep durable and explicitly confirmed knowledge in `01_Base_Memory`. / 将长期有效且明确确认的知识保存在 `01_Base_Memory`。  
5. Let temporary or uncertain material stay in `03_Short_Term_Memory` until review. / 让临时或不确定的内容暂存在 `03_Short_Term_Memory`，等待审查。  
6. Rebuild indexes and generate context when preparing future AI sessions. / 在准备后续 AI 会话时重建索引并生成上下文。  
7. Archive outdated memory without deleting useful history. / 对过时内容进行归档，同时保留有价值的历史记录。  

---

## Quick Start / 快速开始

1. Clone the repository. / 克隆仓库。  
2. Initialize or repair the local structure. / 初始化或修复本地结构。  

```bash
python3 memory.py init
```

3. Run the test suite to verify the local runtime. / 运行测试套件，验证本地运行时。  

```bash
python3 -m unittest discover -s tests
```

4. Create or resolve a project memory space. / 创建或解析一个项目记忆空间。  

```bash
python3 memory.py add-project "Example Project"
```

5. Start capturing memory through the CLI. / 开始通过命令行捕获记忆。  

```bash
python3 memory.py add --memory-type short --module inspiration --content "First local memory note"
```

6. Connect an external agent by calling `capture-turn` at the end of each task. / 通过在每次任务结束时调用 `capture-turn`，将外部 agent 接入记忆运行时。  

---

## Verification / 验证方式

Run the local test suite with:

使用以下命令运行本地测试套件：

```bash
python3 -m unittest discover -s tests -v
```

The tests cover runtime routing, marker-safe writes, duplicate handling, project index updates, base-memory conflict behavior, turn capture, and index rebuilding.

测试覆盖运行时路由、标记区块安全写入、重复内容处理、项目索引更新、基础记忆冲突处理、回合捕获和索引重建。

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
- memory event logs / 记忆事件日志
- content hash registries / 内容哈希注册表
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
01_Base_Memory/*.md
02_Project_Memory/P_*/**
03_Short_Term_Memory/**
04_Context_Builder/generated_contexts/**

# Runtime logs and indexes
00_System/logs/**
00_System/indexes/content_hashes.json

# Secrets
.env
*.key
*.token

# Local outputs
*.log
*.tmp
```

You may keep only sanitized examples in the repository and store real working memory in ignored local files or ignored project folders.

你也可以只在仓库中保留脱敏示例，而把真实工作记忆放在被忽略的本地文件或项目目录中。

---

## Roadmap / 路线图

- stronger agent integration examples / 更完整的 agent 集成示例
- richer prompt libraries / 更丰富的提示模板库
- stronger schemas for memory objects / 更完善的记忆对象 Schema
- better context builder workflows / 更成熟的上下文构建流程
- review and migration utilities for short-term memory / 面向短期记忆的审查与迁移工具
- integrations with local AI tooling, IDE workflows, and browser agents / 与本地 AI 工具、IDE 工作流和浏览器 agent 的集成能力

---

## Contributing / 贡献方式

Contributions are welcome, especially around documentation, templates, schemas, tests, workflow examples, local tooling, and agent integration patterns. Please do not submit any real personal memory or sensitive project material.

欢迎围绕文档、模板、Schema、测试、工作流示例、本地工具和 agent 集成模式进行贡献。请不要提交任何真实个人记忆或敏感项目材料。

---

## License / 许可证

Released under the MIT License.  
基于 MIT License 开源。
