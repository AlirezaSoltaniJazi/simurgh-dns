# Code Style Reference — simurgh-dns

## Import Order

Three groups separated by blank lines: stdlib → third-party → local.

```python
# stdlib
import asyncio
import struct
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path

# third-party
from pydantic_settings import BaseSettings

# local
from simurgh.cache import DNSCache
from simurgh.models import ResolveResult
from simurgh.protocol.types import DNSRecord, RecordType
```

**Rules**:
- `import X` statements before `from X import Y` within each group
- Alphabetical within each group
- No relative imports — always `from simurgh.module import X`
- No wildcard imports (`from X import *`)
- No unused imports (enforced by ruff)

## Type Hints

Modern Python 3.10+ syntax exclusively.

```python
# Correct
def resolve(
    domain: str,
    record_type: int,
    timeout: float | None = None,
) -> ResolveResult:
    ...

# Correct — lowercase generics
records: list[DNSRecord] = []
cache: dict[str, CacheEntry] = {}
handlers: tuple[Callable, ...] = ()

# Correct — union syntax
value: str | int | None = None

# WRONG — never use these
from typing import Optional, List, Dict, Tuple  # WRONG
records: List[DNSRecord]  # WRONG
value: Optional[str]  # WRONG
```

**Advanced type patterns**:

```python
from collections.abc import Callable, Awaitable, AsyncIterator

# Callback types
OnProgress = Callable[[str, int], None]
AsyncHandler = Callable[[bytes], Awaitable[bytes]]

# Generic with constraints
from typing import TypeVar

T = TypeVar("T")

def first_or_none(items: list[T]) -> T | None:
    return items[0] if items else None
```

## Naming Conventions

| Category       | Convention           | Example                                    |
| -------------- | -------------------- | ------------------------------------------ |
| Modules        | `snake_case.py`      | `dns_cache.py`, `record_types.py`          |
| Classes        | `PascalCase`         | `DNSQuery`, `CacheEntry`, `RecordType`     |
| Functions      | `snake_case`         | `parse_header`, `resolve_query`            |
| Private        | `_snake_case`        | `_validate_packet`, `_evict_expired`       |
| Constants      | `SCREAMING_SNAKE`    | `DEFAULT_TTL`, `MAX_PACKET_SIZE`           |
| Type aliases   | `PascalCase`         | `RecordParser`, `OnProgress`               |
| CLI commands   | `kebab-case`         | `start-server`, `flush-cache`              |
| Test classes   | `TestPascalCase`     | `TestDNSParser`, `TestCacheEviction`       |
| Test functions | `test_snake_case`    | `test_parses_a_record`, `test_cache_miss`  |
| Fixtures       | `snake_case`         | `dns_query`, `mock_server`, `sample_config` |

## Formatting Rules

```python
# Line length: 88 characters (ruff default)

# Trailing commas on multi-line structures
config = ServerConfig(
    host="127.0.0.1",
    port=5353,
    upstream="8.8.8.8",  # trailing comma
)

# Double quotes for strings (ruff default)
name = "example.com"
log_msg = f"Resolved {name} in {elapsed:.2f}ms"

# Dataclass field ordering: required fields first, then defaults
@dataclass(frozen=True, slots=True)
class DNSQuestion:
    name: str
    qtype: RecordType
    qclass: int = 1

# Function signature formatting (break after 88 chars)
async def resolve_query(
    domain: str,
    record_type: RecordType,
    timeout: float | None = None,
    use_cache: bool = True,
) -> ResolveResult:
    ...
```

## Docstrings

Google-style, selective usage:

```python
"""Module one-liner describing purpose."""


def parse_header(data: bytes) -> dict[str, int]:
    """Parse DNS header from raw bytes.

    Args:
        data: Raw DNS packet bytes (minimum 12 bytes).

    Returns:
        Dictionary with header fields: id, flags, qr, opcode, etc.

    Raises:
        ValueError: If data is shorter than DNS header size.
    """
    ...


@dataclass(frozen=True, slots=True)
class DNSRecord:
    """A single DNS resource record."""
    ...  # One-liner is enough for simple dataclasses
```

## ruff Configuration

```toml
[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "RUF",  # ruff-specific rules
]

[tool.ruff.lint.isort]
known-first-party = ["simurgh"]
```
