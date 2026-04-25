#!/usr/bin/env python3
"""Compatibility wrapper for writing memory through the unified runtime."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory_core import add_manual_memory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a memory event.")
    parser.add_argument("--memory-type", default="short")
    parser.add_argument("--content", required=True, help="Memory content to write.")
    parser.add_argument("--project-name")
    parser.add_argument("--field")
    parser.add_argument("--module")
    parser.add_argument("--subtype")
    parser.add_argument("--title")
    parser.add_argument("--summary")
    parser.add_argument("--tags", default="", help="Comma-separated tags.")
    parser.add_argument("--importance", type=int, default=3)
    parser.add_argument("--confidence", type=int, default=3)
    parser.add_argument("--source", default="manual")
    parser.add_argument("--privacy-level", default="local_private")
    parser.add_argument("--session-id")
    parser.add_argument("--turn-id")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root. Defaults to the current repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tags = [item.strip() for item in args.tags.split(",") if item.strip()]
    result = add_manual_memory(
        args.root.resolve(),
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


if __name__ == "__main__":
    raise SystemExit(main())
