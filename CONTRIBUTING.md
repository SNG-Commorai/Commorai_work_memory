# Contributing

Thanks for helping improve Commorai Work Memory.

## Scope

This repository is for the framework, prompts, schemas, templates, examples, and local tooling only. Do not open pull requests that include real memory data, real project files, generated contexts, secrets, or logs.

## Contribution Guidelines

1. Keep the project local-first and privacy-first.
2. Prefer standard library tooling for scripts when possible.
3. Use sanitized examples only.
4. Update related docs when behavior changes.
5. Run `python3 scripts/scan_sensitive_files.py` before opening a PR or pushing.

## Pull Request Checklist

- No real memory content is included.
- No `.env`, tokens, credentials, or private logs are included.
- New scripts operate on the current project directory only.
- Documentation matches the implementation.
