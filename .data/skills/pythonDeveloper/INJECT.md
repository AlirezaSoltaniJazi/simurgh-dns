# pythonDeveloper — Quick Reference

**Stack**: Python 3.13+, uv, hatchling, pytest, ruff, asyncio, struct

**Entry point**: `simurgh = "simurgh.cli:main"` in pyproject.toml

**Source**: `src/simurgh/` — DNS server/library with async networking, protocol parsing, caching, filtering

**Key modules**: `server.py` (async UDP/TCP), `resolver.py` (query logic), `protocol/` (DNS parsing/building), `cache.py` (TTL cache), `config.py` (pydantic-settings), `models.py` (result dataclasses)

## Rules — ALWAYS

- Absolute imports only — never relative
- `pathlib.Path` — never `os.path`
- Modern type hints: `str | None`, `dict[str, X]`, `list[X]`
- Result dataclasses for fallible operations — never raise for expected failures
- `asyncio` for all network I/O — never blocking calls in async context
- Network byte order (`!` prefix) for all `struct` operations
- Frozen dataclasses for DNS protocol types
- ruff for formatting and linting
- `uv add` for dependencies — never `pip install`

## Rules — NEVER

- `os.path` — use `pathlib.Path`
- `Optional[X]` — use `X | None`
- `Dict`, `List`, `Tuple` from typing — use lowercase builtins
- Relative imports — use absolute
- `pip install` — use `uv add`
- `setup.py` or `requirements.txt` — use `pyproject.toml`
- Blocking I/O in async — use `asyncio` equivalents
- `print()` for output — use structured logging or rich
- DNS parsing without validation — always check packet length/format first

## Sub-Agents

- **code-reviewer**: Read-only code analysis (Tools: Read, Glob, Grep)
- **test-writer**: Pytest generation (Tools: Read, Edit, Write, Glob, Grep, Bash)
- **dependency-auditor**: Security audit (Tools: Read, Glob, Grep, Bash)

## Self-Learning

All corrections → [LEARNED.md](LEARNED.md) `## Corrections` section. All preferences → `## Preferences`. All discovered conventions → `## Discovered Conventions`. Format: `- YYYY-MM-DD: rule`.
