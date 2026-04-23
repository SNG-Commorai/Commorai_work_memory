# Research Note: In-Depth Research on the MemoryOS Project

- Created At: 2026-04-22T13:49:51+08:00
- Memory ID: 5e0e7434-e0de-4ad1-8baf-b519076953fa
- Type: project
- Field/Module:
- Importance: 5
- Confidence: 4
- Status: active
- Tags: MemoryOS, AI-Memory, EMNLP2025, memory_operating_system, comparative_research
- Related Project: Commorai_work_memory

## Content
## In-Depth Research on the MemoryOS Project

### Basic Information
- **Project:** MemoryOS (Memory OS of AI Agent)
- **GitHub:** https://github.com/BAI-LAB/MemoryOS
- **Paper:** arXiv:2506.06326 → EMNLP 2025 Oral
- **Team:** BAI-LAB (team led by Associate Professor Bai Ting at Beijing University of Posts and Telecommunications)

### Core Positioning
Provides a memory operating system for personalized AI agents, addressing the lack of long-term memory and personalization caused by the fixed context window of LLMs.

### Architecture Design (Three Storage Layers + Four Core Modules)

**Three-Layer Storage Architecture:**
1. Short-term Memory — recent interactions, managed with FIFO over the conversation chain with a default capacity of 7 turns.
2. Mid-term Memory — consolidates short-term interactions and promotes them to long-term memory based on a salience threshold.
3. Long-term Personal Memory — a user profile plus knowledge base, organized with a segmented paging strategy.

**Four Core Modules:** Storage / Updating / Retrieval / Generation

### Technical Characteristics
- Embedding: BGE-M3 / Qwen3-Embedding / all-MiniLM-L6-v2
- Vector database: ChromaDB optional
- Model support: OpenAI / Anthropic / DeepSeek-R1 / Qwen / vLLM
- Deployment options: PyPI (`pip install memoryos-pro`) / MCP Server / Docker / Playground
- MCP integrations: agent clients such as Claude Desktop, Cline, and Cursor

### Performance (LoCoMo Benchmark)
- F1 improvement: average +49.11% (vs. baseline on GPT-4o-mini)
- BLEU-1 improvement: average +46.18%

### Key Comparison Points With Commorai_work_memory
- MemoryOS: automated memory management with automatic extraction, classification, and promotion, relying on LLMs plus embeddings
- Commorai_work_memory: manually rule-driven, where the agent decides the type and writes it into a pure local file system
- MemoryOS strengths: semantic retrieval, automatic memory promotion, and vector similarity matching
- Commorai_work_memory strengths: fully transparent and auditable, no external dependencies, and fine-grained human control

### Areas For Deeper Follow-Up
- [ ] Comparative analysis with Mem0 and Zep
- [ ] Implementation details of the segmented paging strategy
- [ ] MCP protocol integration approach
- [ ] Playground platform experience
