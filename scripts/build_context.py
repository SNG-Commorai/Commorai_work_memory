#!/usr/bin/env python3
"""Build a local context file using canonical event metadata first."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory_core import load_canonical_events

TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml"}
SKIP_NAMES = {"README.md", ".gitkeep"}


@dataclass
class Match:
    layer_name: str
    path: Path
    score: int
    excerpt: str


def normalize_terms(values: list[str]) -> list[str]:
    terms: list[str] = []
    for value in values:
        cleaned = value.strip().lower()
        if cleaned and cleaned not in terms:
            terms.append(cleaned)
    return terms


def task_terms(task: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_\-\u4e00-\u9fff]{2,}", task.lower())
    return normalize_terms(tokens)


def excerpt_for(text: str, terms: list[str], width: int = 320) -> str:
    lower_text = text.lower()
    start = 0
    for term in terms:
        index = lower_text.find(term)
        if index >= 0:
            start = max(index - 80, 0)
            break
    snippet = text[start : start + width].strip()
    snippet = re.sub(r"\s+", " ", snippet)
    return snippet or "(empty match)"


def event_score(event, terms: list[str], project_name: str | None) -> int:
    searchable = "\n".join(
        [
            event.title,
            event.summary,
            event.content[:500],
            event.field_or_module or "",
            " ".join(event.tags),
            event.target_path,
            event.project_name or "",
        ]
    ).lower()
    score = sum(1 for term in terms if term and term in searchable)
    if project_name and event.project_name and event.project_name.lower() == project_name.lower():
        score += 3
    if event.status == "duplicate_skipped":
        score -= 2
    return score


def find_matches(root: Path, task: str, project_name: str | None, keywords: list[str], tags: list[str], limit: int) -> list[Match]:
    terms = normalize_terms(keywords + tags + task_terms(task))
    if project_name:
        terms = normalize_terms([project_name] + terms)

    matches: list[Match] = []
    events = load_canonical_events(root)
    for event in events:
        score = event_score(event, terms, project_name)
        if score <= 0:
            continue
        target = root / event.target_path
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8")
        if event.memory_type == "base_memory":
            layer_name = "Base Memory"
        elif event.memory_type == "project_memory":
            layer_name = "Project Memory"
        else:
            layer_name = "Short-Term Memory"
        matches.append(
            Match(
                layer_name=layer_name,
                path=target,
                score=score,
                excerpt=excerpt_for(text, terms),
            )
        )

    deduped: dict[Path, Match] = {}
    for match in matches:
        current = deduped.get(match.path)
        if current is None or match.score > current.score:
            deduped[match.path] = match
    selected = sorted(deduped.values(), key=lambda item: (-item.score, str(item.path)))
    if selected:
        return selected[:limit]
    return fallback_file_matches(root, terms, project_name, limit)


def fallback_file_matches(root: Path, terms: list[str], project_name: str | None, limit: int) -> list[Match]:
    layers = [
        ("Base Memory", root / "01_Base_Memory"),
        ("Project Memory", root / "02_Project_Memory"),
        ("Short-Term Memory", root / "03_Short_Term_Memory"),
    ]
    matches: list[Match] = []
    for layer_name, layer_root in layers:
        if not layer_root.exists():
            continue
        for path in sorted(layer_root.rglob("*")):
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES or path.name in SKIP_NAMES:
                continue
            text = path.read_text(encoding="utf-8")
            searchable = f"{path.relative_to(root)}\n{text}".lower()
            score = sum(1 for term in terms if term and term in searchable)
            if project_name and project_name.lower() in searchable:
                score += 2
            if score <= 0:
                continue
            matches.append(
                Match(
                    layer_name=layer_name,
                    path=path,
                    score=score,
                    excerpt=excerpt_for(text, terms),
                )
            )
    matches.sort(key=lambda item: (-item.score, str(item.path)))
    return matches[:limit]


def render_section(root: Path, title: str, matches: list[Match]) -> str:
    selected = [item for item in matches if item.layer_name == title]
    if not selected:
        return "- No matching items found.\n"
    lines = []
    for item in selected:
        relative = item.path.relative_to(root)
        lines.append(f"- `{relative}` (score: {item.score})")
        lines.append(f"  {item.excerpt}")
    return "\n".join(lines) + "\n"


def build_context_file(
    *,
    root: Path,
    task: str,
    project_name: str | None,
    keywords: list[str],
    tags: list[str],
    limit: int,
) -> tuple[Path, int]:
    matches = find_matches(
        root=root,
        task=task,
        project_name=project_name,
        keywords=keywords,
        tags=tags,
        limit=limit,
    )
    output_dir = root / "04_Context_Builder" / "generated_contexts"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_slug = re.sub(r"[^a-z0-9]+", "-", task.lower()).strip("-")[:40] or "context"
    output_path = output_dir / f"context_{timestamp}_{task_slug}.md"
    content = (
        "# Generated Context\n\n"
        "## Task\n\n"
        f"{task}\n\n"
        "## Base Memory Context\n\n"
        f"{render_section(root, 'Base Memory', matches)}\n"
        "## Project Memory Context\n\n"
        f"{render_section(root, 'Project Memory', matches)}\n"
        "## Short-Term Memory Context\n\n"
        f"{render_section(root, 'Short-Term Memory', matches)}\n"
        "## Constraints\n\n"
        "- Generated locally from canonical logs and file-based memory.\n"
        "- Retrieval is keyword driven and intentionally conservative.\n"
        "- Review pending-review notes before reusing them.\n\n"
        "## Open Questions\n\n"
        "- Which entries should be migrated, consolidated, or archived after this task?\n"
    )
    output_path.write_text(content, encoding="utf-8")
    return output_path, len(matches)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a local context file.")
    parser.add_argument("--task", required=True, help="Task description for context assembly.")
    parser.add_argument("--project-name", help="Optional project filter.")
    parser.add_argument("--keyword", action="append", default=[], help="Keyword filter. Repeatable.")
    parser.add_argument("--tag", action="append", default=[], help="Tag filter. Repeatable.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum number of matched files.")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root. Defaults to the current repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path, matched_count = build_context_file(
        root=args.root.resolve(),
        task=args.task,
        project_name=args.project_name,
        keywords=args.keyword,
        tags=args.tag,
        limit=max(args.limit, 1),
    )
    print("Context build summary")
    print(f"- output: {output_path.relative_to(args.root.resolve())}")
    print(f"- matched items: {matched_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
