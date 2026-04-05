"""Tests for Windows DNS setter."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from simurgh_dns.platform_dns.windows import WindowsDNSSetter


@pytest.fixture
def setter() -> WindowsDNSSetter:
    return WindowsDNSSetter()


class TestGetActiveInterface:
    @patch("subprocess.run")
    def test_finds_interface(
        self, mock_run: MagicMock, setter: WindowsDNSSetter
    ) -> None:
        mock_run.return_value = MagicMock(
            stdout=(
                'Configuration for interface "Ethernet"\n'
                "    DHCP enabled:            Yes\n"
                "    IP Address:              192.168.1.100\n"
            )
        )
        assert setter.get_active_interface() == "Ethernet"

    @patch("subprocess.run")
    def test_no_active_interface(
        self, mock_run: MagicMock, setter: WindowsDNSSetter
    ) -> None:
        mock_run.return_value = MagicMock(stdout="")
        assert setter.get_active_interface() is None

    @patch("subprocess.run")
    def test_command_not_found(
        self, mock_run: MagicMock, setter: WindowsDNSSetter
    ) -> None:
        mock_run.side_effect = FileNotFoundError
        assert setter.get_active_interface() is None


class TestGetCurrentDns:
    @patch("subprocess.run")
    def test_has_servers(self, mock_run: MagicMock, setter: WindowsDNSSetter) -> None:
        mock_run.return_value = MagicMock(
            stdout="DNS servers:\n    8.8.8.8\n    8.8.4.4\n"
        )
        assert setter.get_current_dns("Ethernet") == [
            "8.8.8.8",
            "8.8.4.4",
        ]

    @patch("subprocess.run")
    def test_dhcp(self, mock_run: MagicMock, setter: WindowsDNSSetter) -> None:
        mock_run.return_value = MagicMock(stdout="DNS configured through DHCP\n")
        assert setter.get_current_dns("Ethernet") == ["(DHCP - automatic)"]


class TestSetDns:
    @patch("subprocess.run")
    def test_single_ip(self, mock_run: MagicMock, setter: WindowsDNSSetter) -> None:
        assert setter.set_dns("Ethernet", ["1.1.1.1"]) is True

    @patch("subprocess.run")
    def test_multiple_ips(self, mock_run: MagicMock, setter: WindowsDNSSetter) -> None:
        assert setter.set_dns("Ethernet", ["1.1.1.1", "1.0.0.1"]) is True
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_failure(self, mock_run: MagicMock, setter: WindowsDNSSetter) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, "netsh")
        assert setter.set_dns("Ethernet", ["1.1.1.1"]) is False


class TestResetDns:
    @patch("subprocess.run")
    def test_success(self, mock_run: MagicMock, setter: WindowsDNSSetter) -> None:
        assert setter.reset_dns("Ethernet") is True

    @patch("subprocess.run")
    def test_failure(self, mock_run: MagicMock, setter: WindowsDNSSetter) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, "netsh")
        assert setter.reset_dns("Ethernet") is False
