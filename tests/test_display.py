"""Tests for simurgh_dns.display."""

from io import StringIO

from rich.console import Console

from simurgh_dns.display import display_results
from simurgh_dns.models import BenchmarkResult


class TestDisplayResults:
    def test_renders_table(self, sample_results: list[BenchmarkResult]) -> None:
        output = StringIO()
        import simurgh_dns.display as display_mod

        original = display_mod.console
        display_mod.console = Console(file=output, force_terminal=True, width=120)
        try:
            display_results(sample_results)
        finally:
            display_mod.console = original

        rendered = output.getvalue()
        assert "FastDNS" in rendered
        assert "TestDNS" in rendered
        assert "FailDNS" in rendered
        assert "FAIL" in rendered

    def test_empty_results(self) -> None:
        output = StringIO()
        import simurgh_dns.display as display_mod

        original = display_mod.console
        display_mod.console = Console(file=output, force_terminal=True, width=120)
        try:
            display_results([])
        finally:
            display_mod.console = original

        rendered = output.getvalue()
        assert "DNS Benchmark Results" in rendered
