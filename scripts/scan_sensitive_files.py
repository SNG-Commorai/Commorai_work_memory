#!/usr/bin/env python3
"""Scan repository candidates for secrets or unsafe files before pushing."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
IGNORED_PREFIXES = (
    ".git/",
    "00_System/logs/",
    "00_System/indexes/",
    "01_Base_Memory/",
    "02_Project_Memory/",
    "03_Short_Term_Memory/",
    "04_Context_Builder/generated_contexts/",
    "99_Archive/",
)
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".gitignore", ".gitattributes"}
FILENAME_RULES = {
    ".env": ".env files must never be committed",
    "credentials.json": "credentials file detected",
    "token.json": "token file detected",
    "memory_events.jsonl": "real memory event log detected",
}
CONTENT_PATTERNS = [
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("API key assignment", re.compile(r"(?i)\bapi[_ -]?key\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{10,}")),
    ("Token assignment", re.compile(r"(?i)\btoken\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{10,}")),
    ("Password assignment", re.compile(r"(?i)\bpassword\b\s*[:=]\s*['\"]?\S{3,}")),
    ("Private key header", re.compile(r"BEGIN (RSA|OPENSSH) PRIVATE KEY")),
    ("JWT-like token", re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")),
    ("Email address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
]


def is_heuristically_ignored(relative: str) -> bool:
    return relative.startswith(IGNORED_PREFIXES)


def list_candidate_files(root: Path) -> tuple[list[Path], int]:
    skipped_ignored = 0
    git_dir = root / ".git"

    if git_dir.exists():
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            files = []
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                relative = line.strip()
                path = root / relative
                if path.is_file():
                    files.append(path)
            return files, skipped_ignored

    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if is_heuristically_ignored(relative):
            skipped_ignored += 1
            continue
        files.append(path)
    return files, skipped_ignored


def is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:2048]
    except OSError:
        return True
    return b"\x00" in chunk


def filename_findings(relative: str) -> list[str]:
    findings: list[str] = []
    name = Path(relative).name
    if name in FILENAME_RULES:
        findings.append(FILENAME_RULES[name])
    if "/logs/" in f"/{relative}/" and not relative.endswith(".gitkeep"):
        findings.append("log file detected")
    if "credentials" in name.lower() and name != "credentials.md":
        findings.append("credentials-like filename detected")
    return findings


def content_findings(path: Path) -> list[str]:
    if path.suffix not in TEXT_SUFFIXES and path.name not in {".gitignore", ".gitattributes"}:
        return []
    if is_binary(path):
        return []

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    findings: list[str] = []
    for description, pattern in CONTENT_PATTERNS:
        if pattern.search(text):
            findings.append(description)
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan candidate files for sensitive content.")
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
    files, skipped_ignored = list_candidate_files(root)

    findings: list[tuple[str, list[str]]] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        reasons = filename_findings(relative) + content_findings(path)
        if reasons:
            findings.append((relative, reasons))

    if findings:
        print("Sensitive scan failed")
        for relative, reasons in findings:
            print(f"- {relative}")
            for reason in reasons:
                print(f"  reason: {reason}")
        print("Do not commit or push until the listed files are removed, ignored, or sanitized.")
        return 1

    print("Sensitive scan passed")
    print(f"- scanned files: {len(files)}")
    print("- ignored local-only paths are expected to stay out of Git.")
    if skipped_ignored:
        print(f"- ignored files skipped in fallback mode: {skipped_ignored}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
