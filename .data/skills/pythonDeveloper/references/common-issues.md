# Common Issues — simurgh-dns

## Import Errors

**ModuleNotFoundError: No module named 'simurgh'**
- Fix: `uv pip install -e .` (editable install for development)
- Verify: `pyproject.toml` has correct `[project.scripts]` and `packages` config

**ImportError: cannot import name 'X' from 'simurgh.Y'**
- Check: circular imports between modules
- Fix: move shared types to `models.py`, import at function level if needed

## Async Gotchas

**RuntimeError: This event loop is already running**
- Cause: calling `asyncio.run()` inside an already running loop
- Fix: use `await` directly, or use `asyncio.create_task()` for concurrent work

**RuntimeWarning: coroutine 'X' was never awaited**
- Cause: calling async function without `await`
- Fix: add `await` before the call, or wrap in `asyncio.create_task()`

**pytest-asyncio: no event loop**
- Cause: missing `asyncio_mode = "auto"` in pytest config
- Fix: add to `pyproject.toml` under `[tool.pytest.ini_options]`

**Task was destroyed but it is pending**
- Cause: not awaiting or cancelling tasks before server shutdown
- Fix: use `asyncio.TaskGroup` or explicitly cancel and await tasks

## struct Errors

**struct.error: unpack requires a buffer of X bytes**
- Cause: packet data shorter than expected format
- Fix: always validate `len(data) >= format.size` before unpacking

**struct.error: pack expected X items for packing (got Y)**
- Cause: wrong number of values for format string
- Fix: count format characters — `H` = 2 bytes unsigned short, `I` = 4 bytes unsigned int

**Incorrect values after unpack**
- Cause: wrong byte order — DNS uses network byte order (big-endian)
- Fix: always use `!` prefix in format strings: `struct.unpack("!HH", data)`

## Dataclass Issues

**TypeError: unhashable type with frozen dataclass**
- Cause: mutable default (e.g., `list`) in frozen dataclass
- Fix: use `field(default_factory=list)` or `field(default_factory=tuple)`

**FrozenInstanceError when modifying**
- Cause: trying to mutate a frozen dataclass
- Fix: use `dataclasses.replace(record, ttl=new_ttl)` to create modified copy

## Network Issues

**OSError: [Errno 48] Address already in use**
- Cause: port still bound from previous run
- Fix: set `SO_REUSEADDR` on socket, or use a different port for testing

**ConnectionRefusedError when querying upstream**
- Cause: upstream DNS server unreachable
- Fix: implement timeout + retry logic, fall back to secondary upstream

**UDP packet truncation**
- Cause: response exceeds 512 bytes (standard UDP DNS limit)
- Fix: set TC (truncated) flag and let client retry over TCP, or implement EDNS

## Configuration Issues

**ValidationError from pydantic-settings**
- Cause: missing or invalid environment variable
- Fix: check `.env` file, ensure `SIMURGH_` prefix on all variables

**Config not loading from .env**
- Cause: wrong `env_file` path or missing `python-dotenv` dependency
- Fix: verify `.env` is in project root, ensure `pydantic-settings[dotenv]` is installed
