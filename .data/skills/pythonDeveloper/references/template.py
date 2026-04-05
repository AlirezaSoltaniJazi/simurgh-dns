"""Module description — one-liner explaining purpose."""

import asyncio
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT: float = 5.0
MAX_RETRIES: int = 3


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ImmutableModel:
    """Immutable data — used for protocol types, config snapshots."""

    name: str
    value: int
    tags: tuple[str, ...] = ()


@dataclass
class MutableModel:
    """Mutable data — used for state, builders, accumulators."""

    items: list[str] = field(default_factory=list)
    count: int = 0
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def do_something(
    name: str,
    timeout: float = DEFAULT_TIMEOUT,
) -> MutableModel:
    """Perform the operation described by this module.

    Args:
        name: The target name to process.
        timeout: Maximum time in seconds to wait.

    Returns:
        MutableModel with results or error.
    """
    try:
        result = await _internal_operation(name, timeout)
        return MutableModel(items=result, count=len(result))
    except TimeoutError:
        return MutableModel(error=f"Timed out after {timeout}s")
    except ValueError as e:
        return MutableModel(error=str(e))


# ---------------------------------------------------------------------------
# Private Helpers
# ---------------------------------------------------------------------------


async def _internal_operation(
    name: str,
    timeout: float,
) -> list[str]:
    """Internal implementation detail — not part of public API."""
    async with asyncio.timeout(timeout):
        # Implementation here
        return [name]
