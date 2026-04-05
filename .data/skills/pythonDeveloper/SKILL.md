---
name: pythonDeveloper
description: >-
  Python development skill for the simurgh-dns project. Covers DNS protocol
  implementation, async networking, binary parsing, module architecture, testing,
  type annotations, caching, error handling, and package management. Activates
  when writing Python code, creating modules, fixing bugs, adding tests, refactoring,
  managing dependencies, or working with DNS protocol, asyncio networking, struct
  parsing, or any src/simurgh/ source file.
compatibility: "Python 3.13+, uv, hatchling, pytest, ruff, asyncio"
metadata:
  author: simurgh-dns
  version: "1.0.0"
  sdlc-phase: development
allowed-tools: Read Edit Write Bash(python:*) Bash(uv:*) Bash(pip:*) Bash(pytest:*) Glob Grep Agent
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: pythonDeveloper skill" at the very start of your response before doing any work.

## When to Use

1. Writing or modifying any Python file under `src/simurgh/`
2. Creating new modules, dataclasses, DNS record types, or protocol handlers
3. Fixing Python bugs, refactoring, or optimizing performance
4. Writing or updating pytest tests under `tests/`
5. Managing dependencies via `uv` or modifying `pyproject.toml`
6. Working with async networking, DNS parsing, caching, or binary I/O

## Do NOT Use

- **Frontend code** (JS/TS, HTML, CSS) — not applicable to this project
- **Infrastructure/DevOps** (Docker, Terraform, CI/CD) — use a dedicated devops skill
- **Mobile development** (Swift/Kotlin) — not applicable to this project

## Architecture

```
src/simurgh/
├── __init__.py             # Package root — version, public API
├── __main__.py             # python -m simurgh entry point
├── cli.py                  # CLI interface (typer/argparse)
├── server.py               # Async UDP/TCP DNS server
├── resolver.py             # Query resolution logic
├── protocol/               # DNS protocol implementation
│   ├── __init__.py
│   ├── parser.py           # Binary DNS packet parsing (struct)
│   ├── builder.py          # DNS response construction
│   ├── types.py            # DNS record types (A, AAAA, CNAME, MX, etc.)
│   └── constants.py        # DNS opcodes, rcodes, flags
├── cache.py                # TTL-aware DNS record cache
├── config.py               # Configuration (pydantic-settings)
├── filters.py              # Query filtering / blocking rules
├── upstream.py             # Upstream resolver forwarding
├── models.py               # Core dataclasses and result types
└── logging.py              # Structured logging setup
```

**Data flow**: DNS query bytes → `protocol.parser` → `resolver` → cache/upstream → `protocol.builder` → response bytes.

**Entry point**: `simurgh = "simurgh.cli:main"` in `pyproject.toml`.

## Key Patterns

| Pattern              | Approach                                          | Key Rule                                              |
| -------------------- | ------------------------------------------------- | ----------------------------------------------------- |
| Result objects       | `@dataclass` with `success`/`error` fields        | Return results from operations, never raise           |
| Binary parsing       | `struct.pack/unpack` with network byte order      | Always use `!` (big-endian) format prefix             |
| Async server         | `asyncio.DatagramProtocol` / `asyncio.start_server` | Non-blocking I/O for all network operations        |
| Frozen dataclasses   | `@dataclass(frozen=True)` for DNS records         | All protocol types are immutable                      |
| TTL caching          | `dict` with expiry timestamps                     | Respect DNS TTL values, evict expired entries         |
| Configuration        | `pydantic-settings` with `.env` support           | All config from environment, never hardcoded          |
| Registry pattern     | Module-level `dict` for record type handlers      | `RECORD_TYPES`, `OPCODES` as registries               |
| Callback progress    | `Callable[[T], None] | None` for streaming events | Stream query logs, stats via callbacks                |

See [references/patterns.md](references/patterns.md) for full code examples.

## Code Style

| Rule                  | Convention                                                       |
| --------------------- | ---------------------------------------------------------------- |
| Python version        | 3.13+ — use latest syntax features                               |
| Formatter/Linter      | ruff (format + lint in one tool)                                 |
| Import style          | Absolute only — never relative imports                           |
| Import order          | stdlib → third-party → local (groups separated by blank line)    |
| Type hints            | Modern syntax: `str | None`, `dict[str, X]`, `list[X]`          |
| Naming — modules      | `snake_case.py`                                                  |
| Naming — classes      | `PascalCase` (e.g., `DNSQuery`, `RecordType`)                   |
| Naming — functions    | `snake_case` with `_private` prefix for internal                 |
| Naming — constants    | `SCREAMING_SNAKE_CASE` (e.g., `RECORD_TYPES`, `DEFAULT_TTL`)    |
| Naming — CLI commands | `kebab-case` (e.g., `start-server`, `flush-cache`)              |
| Paths                 | Always `pathlib.Path` — never `os.path`                          |
| Data models           | `@dataclass` (frozen for immutable, regular for mutable)         |
| Strings               | Double quotes preferred (ruff default)                           |
| Docstrings            | Google-style, selective — module one-liners, function descriptions |
| Line length           | 88 characters (ruff default)                                     |

See [references/code-style.md](references/code-style.md) for full formatting examples.

## Common Recipes

1. **Add a new DNS record type**: Add dataclass to `protocol/types.py` → register in `RECORD_TYPES` dict → add parser in `protocol/parser.py` → add builder in `protocol/builder.py` → add tests
2. **Add a CLI command**: Add command function in `cli.py` → implement handler → call core module → format output
3. **Add upstream resolver**: Create handler in `upstream.py` → implement async query forwarding → add timeout/retry logic → register in config
4. **Create a result dataclass**: Define `@dataclass` with descriptive fields → include optional `error: str | None = None` → return from core function instead of raising
5. **Add a cache strategy**: Implement in `cache.py` → respect TTL → add eviction policy → add metrics callback
6. **Add a new module**: Create `src/simurgh/module_name.py` → add module docstring → use absolute imports → export via `__init__.py` if public API

## Testing Standards

| Rule              | Convention                                                  |
| ----------------- | ----------------------------------------------------------- |
| Framework         | pytest with `asyncio_mode = "auto"`                         |
| Test file naming  | `test_{module}.py` in `tests/`                              |
| Fixture location  | `conftest.py` for shared, test file for local               |
| Key fixtures      | `dns_query`, `dns_response`, `mock_server`, `sample_config` |
| Temp filesystem   | `tmp_path` + structured directories for integration tests   |
| Mocking           | `unittest.mock.patch` for network, upstream resolvers       |
| Test organization | Class-based: `class TestFeatureName`                        |
| Async tests       | `async def test_*` — auto mode handles event loop           |
| What to mock      | Network calls, upstream DNS, filesystem when expensive      |
| What NOT to mock  | Dataclass construction, protocol parsing, pure functions    |

See [references/test-patterns.md](references/test-patterns.md) for full test examples.

## Performance Rules

- Use `__slots__` on frequently instantiated dataclasses (DNS records, queries)
- Use `struct.Struct` objects for repeated pack/unpack operations (pre-compiled)
- Prefer `asyncio.DatagramProtocol` over high-level APIs for UDP performance
- Implement connection pooling for upstream TCP resolvers
- Use generators for large zone file parsing — avoid materializing full lists
- Cache compiled struct formats and frequently resolved records
- Use `asyncio.TaskGroup` for concurrent upstream queries

## Security

- Validate all incoming DNS packets before parsing (length, format)
- Implement rate limiting to prevent DNS amplification attacks
- Use `shlex.quote()` for shell argument construction
- Never embed secrets in source — use environment variables
- Sanitize log output — never log full raw packets in production
- Validate upstream resolver addresses before connecting

See [references/security-checklist.md](references/security-checklist.md) for detailed checklists.

## Anti-Patterns

| Anti-Pattern                             | Why It's Wrong                                                 |
| ---------------------------------------- | -------------------------------------------------------------- |
| Using `os.path` instead of `pathlib`     | Project standardized on `Path` — consistency and readability   |
| Raising exceptions for expected failures | Use result dataclasses — callers should handle expected errors  |
| Using `Optional[X]` from typing          | Use `X | None` — modern Python 3.10+ union syntax              |
| Using `Dict`, `List` from typing         | Use lowercase `dict`, `list` — deprecated uppercase generics   |
| Using relative imports                   | Project uses absolute imports exclusively                      |
| Using `pip install`                      | Use `uv add` — project standardized on uv package manager     |
| Using `setup.py` or `requirements.txt`  | Use `pyproject.toml` — single source of truth                  |
| Blocking I/O in async context            | Use `asyncio` APIs — blocking calls freeze the event loop      |
| Parsing DNS without validation           | Always validate packet length/format before struct.unpack      |
| Using `print()` for user output          | Use structured logging or rich for formatted output            |

## Code Generation Rules

1. **Read before writing** — always read the target file and related modules before making changes
2. **Match existing style** — follow ruff formatting and import conventions exactly
3. **Return results** — new functions that can fail must return result dataclasses, not raise
4. **Type everything** — use modern type hints on all function signatures and class fields
5. **Test alongside** — when creating a module, create its test file with fixtures and basic cases
6. **On correction** — acknowledge, restate as rule, apply to all subsequent actions, write to [LEARNED.md](LEARNED.md)
7. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then project files, ask ONE question, write preference to [LEARNED.md](LEARNED.md)

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode       | Detection Signal                                                  | Behavior                                                            |
| ---------- | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| Diagnostic | "ImportError", "TypeError", "test fails", "broken", stack trace   | Read error context, trace to root cause, fix with minimal changes   |
| Efficient  | "another record type like X", "add field to Y", "same pattern as" | Minimal explanation, replicate existing patterns, apply conventions  |
| Teaching   | "what does this do", "explain protocol", "how does async work"    | Explain with references to project examples, link to references/    |
| Review     | "review this", "check my code", "audit module"                   | Read-only analysis, check against conventions, report without changes |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections → `## Corrections` section
- Preferences → `## Preferences` section
- Discovered conventions → `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Sub-Agent Delegation

| Agent              | Role                                           | Spawn When                                       | Tools                          |
| ------------------ | ---------------------------------------------- | ------------------------------------------------ | ------------------------------ |
| code-reviewer      | Read-only Python code analysis, type audit     | PR review, refactoring assessment, type audit    | Read Glob Grep                 |
| test-writer        | Pytest test generation following project style | "write tests for X", new module, coverage gaps   | Read Edit Write Glob Grep Bash |
| dependency-auditor | Dependency analysis and security audit         | Dependency update, security audit, compatibility | Read Glob Grep Bash            |

**Delegation rules**: Spawn when task is self-contained and won't need follow-up context. Never delegate tasks requiring architectural decisions. See [agents/](agents/) for full definitions.

## Freedom Levels

| Level             | Scope                                                                          | Examples                                                      |
| ----------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| **MUST** follow   | Result objects, absolute imports, pathlib, type hints, ruff, uv, async I/O     | "MUST return result dataclass", "MUST use absolute imports"   |
| **SHOULD** follow | Google docstrings, frozen dataclasses for immutable, class-based test grouping | "SHOULD add module docstring", "SHOULD freeze DNS records"    |
| **CAN** customize | Fixture organization, docstring detail level, test helper placement            | "CAN group fixtures by feature", "CAN use inline test helpers" |

## References

| File                                                                     | Description                                                   |
| ------------------------------------------------------------------------ | ------------------------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                 | **Auto-updated.** Corrections, preferences, conventions       |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference (hallucination firewall)        |
| [references/patterns.md](references/patterns.md)                         | Result objects, DNS parsing, async, caching patterns          |
| [references/code-style.md](references/code-style.md)                     | Import order, type hints, naming, formatting with examples    |
| [references/test-patterns.md](references/test-patterns.md)               | Pytest fixtures, async tests, mocking patterns with examples  |
| [references/security-checklist.md](references/security-checklist.md)     | Input validation, DNS security, secret management checklists  |
| [references/common-issues.md](references/common-issues.md)               | Troubleshooting Python pitfalls, async gotchas, struct errors |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols              |
| [references/template.py](references/template.py)                         | Copy-paste module/class boilerplate                           |
| [assets/pyproject-example.toml](assets/pyproject-example.toml)           | pyproject.toml template with uv + hatchling                   |
| [scripts/validate-python.sh](scripts/validate-python.sh)                 | Python naming + structure convention checker                   |
| [agents/code-reviewer.md](agents/code-reviewer.md)                       | Read-only Python code analysis agent                          |
| [agents/test-writer.md](agents/test-writer.md)                           | Pytest test generation agent                                  |
| [agents/dependency-auditor.md](agents/dependency-auditor.md)             | Dependency analysis and security agent                        |
