#!/usr/bin/env python3
"""Compatibility wrapper for template-based project creation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory_core import create_project_space


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a project memory folder.")
    parser.add_argument("project_name", help="Human-readable project name.")
    parser.add_argument("--stage", default="planning", help="Initial project stage.")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root. Defaults to the current repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = create_project_space(args.root.resolve(), args.project_name, stage=args.stage)
    print("Project summary")
    print(f"- project_id: {result['project_id']}")
    print(f"- project_name: {result['project_name']}")
    print(f"- path: {result['path']}")
    print(f"- stage: {result['stage']}")
    print(f"- project_index: {result['project_index']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
