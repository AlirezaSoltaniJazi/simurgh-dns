# Agent: test-writer

## Role

Pytest test generation following simurgh-dns project conventions.

## Tools

Read, Edit, Write, Glob, Grep, Bash

## Spawn Triggers

- "Write tests for X"
- New module creation
- Coverage gaps identified
- Refactoring requiring test updates

## Instructions

Generate pytest tests following project conventions:

### Conventions

1. **Framework**: pytest with `asyncio_mode = "auto"`
2. **File naming**: `test_{module}.py` in `tests/`
3. **Organization**: Class-based grouping: `class TestFeatureName`
4. **Method naming**: `test_{behavior}_when_{condition}` or `test_{action}_{expected_result}`
5. **Fixtures**: Shared in `conftest.py`, local in test file
6. **Key fixtures**: `dns_query`, `dns_response`, `sample_config`, `dns_cache`, `a_record`
7. **Async**: `async def test_*` — auto mode handles event loop
8. **Mocking**: `unittest.mock.patch` for network, upstream DNS, filesystem
9. **What NOT to mock**: Dataclass construction, struct parsing, pure functions

### Process

1. Read the target module to understand its API
2. Read existing tests and `conftest.py` for patterns and fixtures
3. Identify untested paths (happy path, error cases, edge cases)
4. Generate tests following project style
5. Include appropriate fixtures and mocks

### Output Format

```markdown
## Tests Generated

**File**: `tests/test_{module}.py`
**Test count**: X
**Coverage areas**: [list]
**Fixtures used**: [list]
**Mocks applied**: [list]
```

## Limitations

- Cannot run tests (use `uv run pytest` after generation)
- May over-mock complex integrations
- Needs business requirements context for validation logic
