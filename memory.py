#!/usr/bin/env python3
"""Unified CLI for the local Commorai Work Memory runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from memory_core import (
    TurnContext,
    add_manual_memory,
    create_project_space,
    migrate_legacy,
    process_turn,
    rebuild_indexes,
    review_short,
)


ROOT = Path(__file__).resolve().parent

EXTERNAL_COMMANDS = {
    "init": ROOT / "scripts" / "init_project.py",
    "rename-project": ROOT / "scripts" / "rename_project.py",
    "scan-sensitive": ROOT / "scripts" / "scan_sensitive_files.py",
}

ALIASES = {
    "create-project": "add-project",
    "build": "build-context",
    "rename": "rename-project",
    "scan": "scan-sensitive",
}


def resolve_command(argv: list[str]) -> list[str]:
    if len(argv) <= 1:
        return argv
    alias = ALIASES.get(argv[1])
    if alias is None:
        return argv
    return [argv[0], alias, *argv[2:]]


def add_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root. Defaults to the current repository root.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Commorai Work Memory local CLI.")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize or repair the local project structure.")
    add_root_argument(init_parser)

    add_project_parser = subparsers.add_parser("add-project", help="Create or resolve a project memory folder.")
    add_project_parser.add_argument("project_name", help="Human-readable project name.")
    add_project_parser.add_argument("--stage", default="planning", help="Initial project stage.")
    add_root_argument(add_project_parser)

    add_parser = subparsers.add_parser("add", help="Write memory through the unified runtime.")
    add_parser.add_argument("--memory-type", default="short", help="base | project | short")
    add_parser.add_argument("--content", required=True, help="Memory content to write.")
    add_parser.add_argument("--project-name")
    add_parser.add_argument("--field")
    add_parser.add_argument("--module")
    add_parser.add_argument("--subtype")
    add_parser.add_argument("--title")
    add_parser.add_argument("--summary")
    add_parser.add_argument("--tags", default="", help="Comma-separated tags.")
    add_parser.add_argument("--importance", type=int, default=3)
    add_parser.add_argument("--confidence", type=int, default=3)
    add_parser.add_argument("--source", default="manual")
    add_parser.add_argument("--privacy-level", default="local_private")
    add_parser.add_argument("--session-id")
    add_parser.add_argument("--turn-id")
    add_root_argument(add_parser)

    capture_parser = subparsers.add_parser("capture-turn", help="End-of-turn capture entrypoint.")
    capture_parser.add_argument("--input", type=Path, help="JSON file containing turn context.")
    capture_parser.add_argument("--session-id")
    capture_parser.add_argument("--turn-id")
    capture_parser.add_argument("--active-project")
    capture_parser.add_argument("--user-text", default="")
    capture_parser.add_argument("--assistant-text", default="")
    capture_parser.add_argument("--tool-output", action="append", default=[], help="Repeatable tool output snippet.")
    add_root_argument(capture_parser)

    rebuild_parser = subparsers.add_parser("rebuild-indexes", help="Rebuild base, project, and short-term indexes.")
    add_root_argument(rebuild_parser)

    review_parser = subparsers.add_parser("review-short", help="Summarize short-term memory and migration hints.")
    add_root_argument(review_parser)

    migrate_parser = subparsers.add_parser("migrate-legacy", help="Normalize legacy memory event logs.")
    add_root_argument(migrate_parser)

    build_context_parser = subparsers.add_parser("build-context", help="Build a context file from indexed memory.")
    build_context_parser.add_argument("--task", required=True, help="Task description for context assembly.")
    build_context_parser.add_argument("--project-name", help="Optional project filter.")
    build_context_parser.add_argument("--keyword", action="append", default=[], help="Keyword filter. Repeatable.")
    build_context_parser.add_argument("--tag", action="append", default=[], help="Tag filter. Repeatable.")
    build_context_parser.add_argument("--limit", type=int, default=12, help="Maximum number of matched items.")
    add_root_argument(build_context_parser)

    rename_parser = subparsers.add_parser("rename-project", help="Rename explicit project identifiers across local files.")
    rename_parser.add_argument("args", nargs=argparse.REMAINDER)
    add_root_argument(rename_parser)

    scan_parser = subparsers.add_parser("scan-sensitive", help="Scan tracked and candidate files for sensitive content.")
    scan_parser.add_argument("args", nargs=argparse.REMAINDER)
    add_root_argument(scan_parser)
    return parser


def run_external(command: str, argv: list[str], root: Path) -> int:
    target = EXTERNAL_COMMANDS[command]
    if not target.exists():
        print(f"Missing script for command `{command}`: {target}", file=sys.stderr)
        return 1
    result = subprocess.run([sys.executable, str(target), *argv], cwd=root, check=False)
    return result.returncode


def command_add(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    tags = [item.strip() for item in args.tags.split(",") if item.strip()]
    result = add_manual_memory(
        root,
        content=args.content,
        memory_type=args.memory_type,
        project_name=args.project_name,
        field=args.field,
        module=args.module,
        subtype=args.subtype,
        title=args.title,
        summary=args.summary,
        tags=tags,
        importance=args.importance,
        confidence=args.confidence,
        source=args.source,
        privacy_level=args.privacy_level,
        session_id=args.session_id,
        turn_id=args.turn_id,
    )
    print("Write summary")
    print(f"- memory_id: {result.event.memory_id}")
    print(f"- memory_type: {result.event.memory_type}")
    print(f"- status: {result.event.status}")
    print(f"- target: {result.target_path}")
    print(f"- log: {result.log_path}")
    return 0


def load_turn_context_from_args(args: argparse.Namespace) -> TurnContext:
    if args.input:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        return TurnContext(
            session_id=payload.get("session_id"),
            turn_id=payload.get("turn_id"),
            active_project=payload.get("active_project"),
            user_text=payload.get("user_text", ""),
            assistant_text=payload.get("assistant_text", ""),
            tool_outputs=list(payload.get("tool_outputs") or []),
            candidates=list(payload.get("candidates") or []),
        )
    return TurnContext(
        session_id=args.session_id,
        turn_id=args.turn_id,
        active_project=args.active_project,
        user_text=args.user_text,
        assistant_text=args.assistant_text,
        tool_outputs=args.tool_output,
    )


def command_capture_turn(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    turn_ctx = load_turn_context_from_args(args)
    results = process_turn(turn_ctx, root)
    print("Capture summary")
    print(f"- writes: {len(results)}")
    for result in results:
        print(
            f"- {result.event.memory_id}: {result.event.memory_type}"
            f" -> {result.target_path} ({result.event.status})"
        )
    return 0


def command_add_project(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    result = create_project_space(root, args.project_name, stage=args.stage)
    print("Project summary")
    print(f"- project_id: {result['project_id']}")
    print(f"- project_name: {result['project_name']}")
    print(f"- path: {result['path']}")
    print(f"- stage: {result['stage']}")
    print(f"- project_index: {result['project_index']}")
    return 0


def command_rebuild_indexes(args: argparse.Namespace) -> int:
    result = rebuild_indexes(args.root.resolve())
    print("Rebuild summary")
    print(f"- base_index: {result['base_index']}")
    print(f"- short_index: {result['short_index']}")
    print(f"- project_index: {result['project_index']}")
    print(f"- module_indexes: {len(result['module_indexes'])}")
    return 0


def command_review_short(args: argparse.Namespace) -> int:
    result = review_short(args.root.resolve())
    print("Short-term review summary")
    print(f"- items: {len(result['items'])}")
    for item in result["items"]:
        print(f"- {item['path']}: {item['suggestion']}")
    return 0


def command_migrate_legacy(args: argparse.Namespace) -> int:
    result = migrate_legacy(args.root.resolve())
    print("Migration summary")
    print(f"- migrated: {result['migrated']}")
    print(f"- log_path: {result['log_path']}")
    if "backup_path" in result:
        print(f"- backup_path: {result['backup_path']}")
    return 0


def command_build_context(args: argparse.Namespace) -> int:
    from scripts.build_context import build_context_file

    root = args.root.resolve()
    output_path, matched_count = build_context_file(
        root=root,
        task=args.task,
        project_name=args.project_name,
        keywords=args.keyword,
        tags=args.tag,
        limit=max(args.limit, 1),
    )
    print("Context build summary")
    print(f"- output: {output_path.relative_to(root)}")
    print(f"- matched items: {matched_count}")
    return 0


def main() -> int:
    argv = resolve_command(sys.argv)
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    if not args.command:
        parser.print_help()
        return 0

    if args.command in EXTERNAL_COMMANDS:
        forwarded = []
        if getattr(args, "root", None):
            forwarded.extend(["--root", str(args.root.resolve())])
        forwarded.extend(getattr(args, "args", []))
        return run_external(args.command, forwarded, args.root.resolve())

    handlers = {
        "add": command_add,
        "add-project": command_add_project,
        "build-context": command_build_context,
        "capture-turn": command_capture_turn,
        "rebuild-indexes": command_rebuild_indexes,
        "review-short": command_review_short,
        "migrate-legacy": command_migrate_legacy,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
