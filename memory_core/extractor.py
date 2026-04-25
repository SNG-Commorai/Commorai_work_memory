"""Conservative rule-based memory extraction for end-of-turn capture."""

from __future__ import annotations

from .models import MemoryCandidate, TurnContext
from .utils import derive_summary, derive_title


RESEARCH_HINTS = ("研究", "research", "note", "finding", "issue", "insight")
ANALYSIS_HINTS = ("analysis", "分析", "compare", "comparison")
TOOLS_HINTS = ("tool", "script", "cli", "runtime", "writer")
QUESTION_HINTS = ("?", "待确认", "question", "unclear", "unknown", "need to confirm")


def _candidate_from_structured(item: dict, ctx: TurnContext) -> MemoryCandidate:
    content = str(item.get("content") or "").strip()
    return MemoryCandidate(
        content=content,
        memory_type=item.get("memory_type"),
        title=item.get("title"),
        summary=item.get("summary"),
        project_name=item.get("project_name") or ctx.active_project,
        field=item.get("field"),
        module=item.get("module"),
        subtype=item.get("subtype"),
        tags=list(item.get("tags") or []),
        importance=int(item.get("importance") or 3),
        confidence=int(item.get("confidence") or 3),
        source=str(item.get("source") or "auto_turn_flush"),
        privacy_level=str(item.get("privacy_level") or "local_private"),
        status=item.get("status"),
        update_mode=item.get("update_mode"),
        session_id=ctx.session_id,
        turn_id=ctx.turn_id,
        source_event_id=item.get("source_event_id"),
    )


def _infer_project_module(text: str) -> str:
    lower = text.lower()
    if any(token in lower for token in TOOLS_HINTS):
        return "tools"
    if any(token in lower for token in ANALYSIS_HINTS):
        return "analysis"
    if any(token in lower for token in QUESTION_HINTS):
        return "questions"
    return "research"


def extract_candidates(turn_ctx: TurnContext) -> list[MemoryCandidate]:
    if turn_ctx.candidates:
        return [_candidate_from_structured(item, turn_ctx) for item in turn_ctx.candidates if item.get("content")]

    parts = []
    if turn_ctx.user_text.strip():
        parts.append(f"User: {turn_ctx.user_text.strip()}")
    if turn_ctx.assistant_text.strip():
        parts.append(f"Assistant: {turn_ctx.assistant_text.strip()}")
    for output in turn_ctx.tool_outputs:
        cleaned = str(output).strip()
        if cleaned:
            parts.append(f"Tool: {cleaned}")
    joined = "\n".join(parts).strip()
    if not joined:
        return []

    if turn_ctx.active_project:
        module = _infer_project_module(joined)
        return [
            MemoryCandidate(
                content=joined,
                memory_type="project_memory",
                project_name=turn_ctx.active_project,
                module=module,
                title=derive_title(joined),
                summary=derive_summary(joined),
                source="auto_turn_flush",
                session_id=turn_ctx.session_id,
                turn_id=turn_ctx.turn_id,
            )
        ]

    return [
        MemoryCandidate(
            content=joined,
            memory_type="short_term_memory",
            subtype="needs_review",
            title=derive_title(joined),
            summary=derive_summary(joined),
            source="auto_turn_flush",
            status="pending_review",
            session_id=turn_ctx.session_id,
            turn_id=turn_ctx.turn_id,
        )
    ]
