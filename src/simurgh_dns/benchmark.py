"""DNS benchmark engine — queries DNS servers and measures latency."""

import statistics
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

import dns.resolver

from simurgh_dns.models import BenchmarkResult
from simurgh_dns.servers import (
    DEFAULT_MAX_WORKERS,
    DEFAULT_ROUNDS,
    DEFAULT_TIMEOUT,
    DNS_SERVERS,
    TEST_DOMAINS,
)


def query_dns(server_ip: str, domain: str, timeout: float) -> float | None:
    """Query a DNS server for a domain. Returns latency in ms or None on failure."""
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server_ip]
    resolver.lifetime = timeout
    resolver.timeout = timeout

    start = time.perf_counter()
    try:
        resolver.resolve(domain, "A")
        return (time.perf_counter() - start) * 1000
    except Exception:
        return None


def benchmark_server(
    server_ip: str,
    provider: str,
    rounds: int = DEFAULT_ROUNDS,
    timeout: float = DEFAULT_TIMEOUT,
    domains: list[str] | None = None,
) -> BenchmarkResult:
    """Benchmark a single DNS server IP across test domains for N rounds."""
    if domains is None:
        domains = TEST_DOMAINS

    latencies: list[float] = []
    total_queries = 0
    successful = 0

    for _ in range(rounds):
        for domain in domains:
            total_queries += 1
            result = query_dns(server_ip, domain, timeout)
            if result is not None:
                latencies.append(result)
                successful += 1

    if not latencies:
        return BenchmarkResult(
            provider=provider,
            ip=server_ip,
            avg=float("inf"),
            min=float("inf"),
            max=float("inf"),
            reliability=0.0,
            latencies=(),
        )

    return BenchmarkResult(
        provider=provider,
        ip=server_ip,
        avg=statistics.mean(latencies),
        min=min(latencies),
        max=max(latencies),
        reliability=(successful / total_queries) * 100,
        latencies=tuple(latencies),
    )


def run_benchmark(
    rounds: int = DEFAULT_ROUNDS,
    timeout: float = DEFAULT_TIMEOUT,
    max_workers: int = DEFAULT_MAX_WORKERS,
    servers: dict[str, list[str]] | None = None,
    domains: list[str] | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[BenchmarkResult]:
    """Run the full benchmark across all DNS servers concurrently.

    Args:
        rounds: Number of benchmark rounds per server.
        timeout: Timeout in seconds per DNS query.
        max_workers: Maximum concurrent threads.
        servers: DNS servers to benchmark. Defaults to DNS_SERVERS.
        domains: Domains to test against. Defaults to TEST_DOMAINS.
        progress_callback: Called with (completed, total) after each server finishes.

    Returns:
        List of BenchmarkResult sorted by average latency (fastest first).
    """
    if servers is None:
        servers = DNS_SERVERS
    if domains is None:
        domains = TEST_DOMAINS

    tasks: list[tuple[str, str]] = []
    for provider, ips in servers.items():
        for ip in ips:
            tasks.append((ip, provider))

    total = len(tasks)
    results: list[BenchmarkResult] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for ip, provider in tasks:
            future = executor.submit(
                benchmark_server, ip, provider, rounds, timeout, domains
            )
            futures[future] = (ip, provider)

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if progress_callback is not None:
                progress_callback(len(results), total)

    results.sort(key=lambda r: r.avg)
    return results
