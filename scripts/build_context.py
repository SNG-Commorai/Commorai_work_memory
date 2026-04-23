#!/usr/bin/env python3
"""Build a local context file from base, project, and short-term memory."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
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
    tokens = re.findall(r"[A-Za-z0-9_\-]{4,}", task.lower())
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


def iter_text_files(root: Path) -> list[tuple[str, Path]]:
    layers = [
        ("Base Memory", root / "01_Base_Memory"),
        ("Project Memory", root / "02_Project_Memory"),
        ("Short-Term Memory", root / "03_Short_Term_Memory"),
    ]
    files: list[tuple[str, Path]] = []
    for layer_name, layer_root in layers:
        if not layer_root.exists():
            continue
        for path in sorted(layer_root.rglob("*")):
            if path.is_file() and path.suffix in TEXT_SUFFIXES and path.name not in SKIP_NAMES:
                files.append((layer_name, path))
    return files


def find_matches(
    root: Path,
    task: str,
    project_name: str | None,
    keywords: list[str],
    tags: list[str],
    limit: int,
) -> list[Match]:
    terms = normalize_terms(keywords + tags + task_terms(task))
    if project_name:
        terms = normalize_terms([project_name] + terms)

    matches: list[Match] = []
    for layer_name, path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        haystack = f"{path.relative_to(root)}\n{text}".lower()
        score = 0
        for term in terms:
            if term and term in haystack:
                score += 1

        if project_name and project_name.lower() in haystack:
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
    root = args.root.resolve()
    matches = find_matches(
        root=root,
        task=args.task,
        project_name=args.project_name,
        keywords=args.keyword,
        tags=args.tag,
        limit=max(args.limit, 1),
    )

    output_dir = root / "04_Context_Builder" / "generated_contexts"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_slug = re.sub(r"[^a-z0-9]+", "-", args.task.lower()).strip("-")[:40] or "context"
    output_path = output_dir / f"context_{timestamp}_{task_slug}.md"

    content = (
        "# Generated Context\n\n"
        "## Task\n\n"
        f"{args.task}\n\n"
        "## Base Memory Context\n\n"
        f"{render_section(root, 'Base Memory', matches)}\n"
        "## Project Memory Context\n\n"
        f"{render_section(root, 'Project Memory', matches)}\n"
        "## Short-Term Memory Context\n\n"
        f"{render_section(root, 'Short-Term Memory', matches)}\n"
        "## Constraints\n\n"
        "- Generated locally from file-based memory.\n"
        "- Results may contain private material and should remain untracked.\n"
        "- Review low-confidence notes before reusing them.\n\n"
        "## Open Questions\n\n"
        "- Which entries should be migrated, consolidated, or archived after this task?\n\n"
        "## Suggested Agent Instruction\n\n"
        "Use the matched context sections above as local references, but do not expose or commit private memory content.\n"
    )
    output_path.write_text(content, encoding="utf-8")

    print("Context build summary")
    print(f"- output: {output_path.relative_to(root)}")
    print(f"- matched files: {len(matches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
