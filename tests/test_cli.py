"""Tests for simurgh_dns.cli."""

from unittest.mock import MagicMock, patch

import pytest


class TestMainReset:
    @patch("simurgh_dns.cli._handle_reset")
    def test_reset_flag(self, mock_reset: MagicMock) -> None:
        with patch("sys.argv", ["simurgh-dns", "--reset"]):
            from simurgh_dns.cli import main

            main()
            mock_reset.assert_called_once()


class TestMainSet:
    @patch("simurgh_dns.cli._handle_set")
    def test_set_flag(self, mock_set: MagicMock) -> None:
        with patch("sys.argv", ["simurgh-dns", "--set", "1.1.1.1"]):
            from simurgh_dns.cli import main

            main()
            mock_set.assert_called_once_with("1.1.1.1")


class TestMainBenchmark:
    @patch("simurgh_dns.cli._offer_set_dns")
    @patch("simurgh_dns.cli._run_benchmark_with_progress")
    def test_benchmark_default(
        self, mock_bench: MagicMock, mock_offer: MagicMock
    ) -> None:
        mock_bench.return_value = []
        with patch("sys.argv", ["simurgh-dns"]):
            from simurgh_dns.cli import main

            main()
            mock_bench.assert_called_once_with(3, False)
            mock_offer.assert_called_once()

    @patch("simurgh_dns.cli._offer_set_dns")
    @patch("simurgh_dns.cli._run_benchmark_with_progress")
    def test_benchmark_no_set(
        self, mock_bench: MagicMock, mock_offer: MagicMock
    ) -> None:
        mock_bench.return_value = []
        with patch("sys.argv", ["simurgh-dns", "--no-set"]):
            from simurgh_dns.cli import main

            main()
            mock_offer.assert_not_called()

    @patch("simurgh_dns.cli._offer_set_dns")
    @patch("simurgh_dns.cli._run_benchmark_with_progress")
    def test_benchmark_json(self, mock_bench: MagicMock, mock_offer: MagicMock) -> None:
        mock_bench.return_value = []
        with patch("sys.argv", ["simurgh-dns", "--json"]):
            from simurgh_dns.cli import main

            main()
            mock_bench.assert_called_once_with(3, True)
            mock_offer.assert_not_called()


class TestVersion:
    def test_version_flag(self) -> None:
        with (
            patch("sys.argv", ["simurgh-dns", "--version"]),
            pytest.raises(SystemExit, match="0"),
        ):
            from simurgh_dns.cli import main

            main()
