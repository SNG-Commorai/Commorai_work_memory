#!/usr/bin/env python3
"""Safely rename explicit project identifiers across local text files."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py"}
SKIP_PREFIXES = (".git/",)


@dataclass
class PlannedChange:
    path: Path
    content_match: bool
    renamed_path: Path | None


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "project"


def replacement_pairs(args: argparse.Namespace) -> list[tuple[str, str]]:
    pairs = [(args.old_name, args.new_name)]
    if args.old_display and args.new_display:
        pairs.append((args.old_display, args.new_display))
    if args.old_path and args.new_path:
        pairs.append((args.old_path, args.new_path))

    old_slug = slugify(args.old_name)
    new_slug = slugify(args.new_name)
    if old_slug != new_slug:
        pairs.append((old_slug, new_slug))

    return pairs


def is_text_file(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in {"README.md", ".gitignore", ".gitattributes"}


def iter_candidate_files(root: Path, include_ignored: bool) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not is_text_file(path):
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith(SKIP_PREFIXES):
            continue
        if not include_ignored and relative.startswith(
            (
                "00_System/logs/",
                "01_Base_Memory/",
                "02_Project_Memory/",
                "03_Short_Term_Memory/",
                "04_Context_Builder/generated_contexts/",
                "99_Archive/",
            )
        ):
            continue
        files.append(path)
    return files


def preview_changes(root: Path, files: list[Path], pairs: list[tuple[str, str]]) -> list[PlannedChange]:
    changes: list[PlannedChange] = []
    for path in files:
        content_match = False
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for old, _new in pairs:
            if old in text:
                content_match = True
                break

        renamed_path: Path | None = None
        relative_text = path.relative_to(root).as_posix()
        for old, new in pairs:
            if old in relative_text:
                renamed_path = root / relative_text.replace(old, new)
                break

        if content_match or renamed_path is not None:
            changes.append(PlannedChange(path=path, content_match=content_match, renamed_path=renamed_path))
    return changes


def apply_changes(changes: list[PlannedChange], pairs: list[tuple[str, str]]) -> None:
    for change in changes:
        if change.content_match:
            text = change.path.read_text(encoding="utf-8")
            for old, new in pairs:
                text = text.replace(old, new)
            change.path.write_text(text, encoding="utf-8")

    for change in sorted(changes, key=lambda item: len(item.path.parts), reverse=True):
        if change.renamed_path is not None and change.path.exists():
            change.renamed_path.parent.mkdir(parents=True, exist_ok=True)
            change.path.rename(change.renamed_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rename explicit project identifiers.")
    parser.add_argument("--old-name", required=True, help="Exact old project name, such as Legacy_Project_Name.")
    parser.add_argument("--new-name", required=True, help="Exact new project name, such as Modern_Project_Name.")
    parser.add_argument("--old-display", help="Optional old display name.")
    parser.add_argument("--new-display", help="Optional new display name.")
    parser.add_argument("--old-path", help="Optional old absolute path.")
    parser.add_argument("--new-path", help="Optional new absolute path.")
    parser.add_argument("--apply", action="store_true", help="Apply changes after printing the plan.")
    parser.add_argument(
        "--include-ignored",
        action="store_true",
        help="Include local-only memory directories in the rename operation.",
    )
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
    pairs = replacement_pairs(args)
    files = iter_candidate_files(root, include_ignored=args.include_ignored)
    changes = preview_changes(root, files, pairs)

    print("Rename plan")
    print(f"- root: {root}")
    print(f"- files considered: {len(files)}")
    print(f"- files to update: {len(changes)}")

    for change in changes:
        relative = change.path.relative_to(root)
        notes = []
        if change.content_match:
            notes.append("content")
        if change.renamed_path is not None:
            notes.append(f"path -> {change.renamed_path.relative_to(root)}")
        print(f"- {relative}: {', '.join(notes)}")

    if not args.apply:
        print("Dry run only. Re-run with --apply to perform the rename.")
        return 0

    apply_changes(changes, pairs)
    print("Rename complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
