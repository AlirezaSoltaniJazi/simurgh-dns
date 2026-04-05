"""Data models for DNS benchmark results."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    """Result of benchmarking a single DNS server IP."""

    provider: str
    ip: str
    avg: float
    min: float
    max: float
    reliability: float
    latencies: tuple[float, ...]

    @property
    def failed(self) -> bool:
        """Return True if this server failed all queries."""
        return self.avg == float("inf")
