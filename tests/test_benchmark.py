"""Tests for simurgh_dns.benchmark."""

from unittest.mock import MagicMock, patch

from simurgh_dns.benchmark import benchmark_server, query_dns, run_benchmark


class TestQueryDns:
    @patch("simurgh_dns.benchmark.dns.resolver.Resolver")
    def test_successful_query(self, mock_resolver_cls: MagicMock) -> None:
        mock_resolver = MagicMock()
        mock_resolver_cls.return_value = mock_resolver
        result = query_dns("8.8.8.8", "example.com", 3.0)
        assert result is not None
        assert result >= 0

    @patch("simurgh_dns.benchmark.dns.resolver.Resolver")
    def test_failed_query(self, mock_resolver_cls: MagicMock) -> None:
        mock_resolver = MagicMock()
        mock_resolver.resolve.side_effect = Exception("timeout")
        mock_resolver_cls.return_value = mock_resolver
        result = query_dns("0.0.0.0", "example.com", 3.0)
        assert result is None


class TestBenchmarkServer:
    @patch("simurgh_dns.benchmark.query_dns")
    def test_all_successful(self, mock_query: MagicMock) -> None:
        mock_query.return_value = 10.0
        result = benchmark_server(
            "8.8.8.8", "Google", rounds=1, domains=["example.com"]
        )
        assert result.provider == "Google"
        assert result.ip == "8.8.8.8"
        assert result.avg == 10.0
        assert result.reliability == 100.0
        assert not result.failed

    @patch("simurgh_dns.benchmark.query_dns")
    def test_all_failed(self, mock_query: MagicMock) -> None:
        mock_query.return_value = None
        result = benchmark_server("0.0.0.0", "Bad", rounds=1, domains=["example.com"])
        assert result.failed
        assert result.reliability == 0.0

    @patch("simurgh_dns.benchmark.query_dns")
    def test_partial_failure(self, mock_query: MagicMock) -> None:
        mock_query.side_effect = [10.0, None]
        result = benchmark_server(
            "8.8.8.8", "Mixed", rounds=1, domains=["a.com", "b.com"]
        )
        assert result.reliability == 50.0
        assert not result.failed


class TestRunBenchmark:
    @patch("simurgh_dns.benchmark.benchmark_server")
    def test_sorted_by_avg(self, mock_bench: MagicMock) -> None:
        from simurgh_dns.models import BenchmarkResult

        slow = BenchmarkResult("Slow", "1.1.1.1", 100.0, 90.0, 110.0, 100.0, (100.0,))
        fast = BenchmarkResult("Fast", "2.2.2.2", 10.0, 5.0, 15.0, 100.0, (10.0,))
        mock_bench.side_effect = [slow, fast]

        results = run_benchmark(
            servers={"Slow": ["1.1.1.1"], "Fast": ["2.2.2.2"]},
            domains=["example.com"],
            rounds=1,
        )
        assert results[0].provider == "Fast"
        assert results[1].provider == "Slow"

    @patch("simurgh_dns.benchmark.benchmark_server")
    def test_progress_callback(self, mock_bench: MagicMock) -> None:
        from simurgh_dns.models import BenchmarkResult

        result = BenchmarkResult("Test", "1.1.1.1", 10.0, 5.0, 15.0, 100.0, (10.0,))
        mock_bench.return_value = result

        callback = MagicMock()
        run_benchmark(
            servers={"Test": ["1.1.1.1"]},
            domains=["example.com"],
            rounds=1,
            progress_callback=callback,
        )
        callback.assert_called_once_with(1, 1)
