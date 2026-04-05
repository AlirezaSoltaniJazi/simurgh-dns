"""Shared test fixtures."""

import pytest

from simurgh_dns.models import BenchmarkResult


@pytest.fixture
def sample_result() -> BenchmarkResult:
    """A successful benchmark result."""
    return BenchmarkResult(
        provider="TestDNS",
        ip="1.2.3.4",
        avg=25.5,
        min=10.0,
        max=50.0,
        reliability=100.0,
        latencies=(10.0, 25.5, 50.0),
    )


@pytest.fixture
def failed_result() -> BenchmarkResult:
    """A failed benchmark result."""
    return BenchmarkResult(
        provider="FailDNS",
        ip="0.0.0.0",
        avg=float("inf"),
        min=float("inf"),
        max=float("inf"),
        reliability=0.0,
        latencies=(),
    )


@pytest.fixture
def sample_results(
    sample_result: BenchmarkResult, failed_result: BenchmarkResult
) -> list[BenchmarkResult]:
    """A list of mixed benchmark results."""
    fast = BenchmarkResult(
        provider="FastDNS",
        ip="5.6.7.8",
        avg=5.0,
        min=2.0,
        max=10.0,
        reliability=100.0,
        latencies=(2.0, 5.0, 10.0),
    )
    return [fast, sample_result, failed_result]
