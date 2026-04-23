# Security Policy

## Supported Use

Commorai Work Memory is intended for local-first usage. Treat all real memory content as private by default.

## Reporting

If you discover a security issue in the framework, open a private security advisory or contact the maintainer through a non-public channel. Do not include secrets, credentials, personal data, or proprietary files in the report.

## Operational Safety

- Run `python3 scripts/scan_sensitive_files.py` before each push.
- Keep real memory files untracked.
- Do not store API keys, tokens, or credentials in this repository.
- When unsure whether a file is safe to publish, do not commit it.
